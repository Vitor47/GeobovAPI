from __future__ import annotations

import math
from datetime import datetime
from typing import Any

from sqladmin import BaseView, expose
from starlette.requests import Request

from app.adapters.database.session_factory import SessionFactory
from app.adapters.models.cattle import Cattle
from app.adapters.models.company import Company
from app.adapters.repositories.cattle_data_repository import (
    HISTORY_COLLECTION,
    RAW_COLLECTION,
)
from app.core.mongo import get_mongo_db


def _parse_optional_int(value: str | None) -> int | None:
    if value is None or value.strip() == "":
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _format_timestamp(value: Any) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value) if value is not None else ""


def _format_optional_int(value: Any) -> str:
    if value is None:
        return "—"
    return str(int(value))


def _format_optional_float(value: Any, digits: int) -> str:
    if value is None:
        return "—"
    return f"{float(value):.{digits}f}"


class TelemetryReadAdmin(BaseView):
    """Read-only MongoDB telemetry browser for SQLAdmin."""

    name = "Telemetry"
    icon = "fa-solid fa-satellite-dish"
    category = "Tracking"

    @expose("/telemetry", methods=["GET"])
    async def list_page(self, request: Request):  # pylint: disable=too-many-locals
        company_id = _parse_optional_int(request.query_params.get("company_id"))
        cattle_id = _parse_optional_int(request.query_params.get("cattle_id"))
        source = (request.query_params.get("source") or "raw").lower()
        if source not in {"raw", "history", "all"}:
            source = "raw"

        try:
            page = max(int(request.query_params.get("page") or 1), 1)
        except ValueError:
            page = 1
        try:
            page_size = int(request.query_params.get("page_size") or 50)
        except ValueError:
            page_size = 50
        page_size = min(max(page_size, 1), 200)

        query: dict[str, Any] = {}
        if company_id is not None:
            query["company_id"] = company_id
        if cattle_id is not None:
            query["cattle_id"] = cattle_id

        mongo = get_mongo_db()
        skip = (page - 1) * page_size

        if source == "all":
            # Merge a window from both collections, then paginate in memory.
            window = skip + page_size
            raw_docs = list(
                mongo[RAW_COLLECTION].find(query).sort("timestamp", -1).limit(window)
            )
            history_docs = list(
                mongo[HISTORY_COLLECTION]
                .find(query)
                .sort("timestamp", -1)
                .limit(window)
            )
            documents = [{**doc, "_source": "raw"} for doc in raw_docs] + [
                {**doc, "_source": "history"} for doc in history_docs
            ]
            documents.sort(
                key=lambda item: item.get("timestamp") or datetime.min,
                reverse=True,
            )
            total = mongo[RAW_COLLECTION].count_documents(query) + mongo[
                HISTORY_COLLECTION
            ].count_documents(query)
            page_docs = documents[skip : skip + page_size]
        else:
            collection_name = RAW_COLLECTION if source == "raw" else HISTORY_COLLECTION
            collection = mongo[collection_name]
            total = collection.count_documents(query)
            page_docs = [
                {**doc, "_source": source}
                for doc in (
                    collection.find(query)
                    .sort("timestamp", -1)
                    .skip(skip)
                    .limit(page_size)
                )
            ]

        total_pages = max(math.ceil(total / page_size), 1) if total else 1
        company_names, cattle_labels = self._load_labels(page_docs)

        rows = []
        for doc in page_docs:
            company_id_value = int(doc.get("company_id") or 0)
            cattle_id_value = int(doc.get("cattle_id") or 0)
            rows.append(
                {
                    "id": str(doc.get("_id")),
                    "source": doc.get("_source"),
                    "company_id": company_id_value,
                    "cattle_id": cattle_id_value,
                    "company_label": company_names.get(
                        company_id_value, f"#{company_id_value}"
                    ),
                    "cattle_label": cattle_labels.get(
                        cattle_id_value, f"#{cattle_id_value}"
                    ),
                    "lat": float(doc.get("lat") or 0),
                    "lon": float(doc.get("lon") or 0),
                    "protocol_version": _format_optional_int(
                        doc.get("protocol_version")
                    ),
                    "sequence": _format_optional_int(doc.get("sequence")),
                    "satellites": _format_optional_int(doc.get("satellites")),
                    "hdop": _format_optional_float(doc.get("hdop"), 1),
                    "rssi": _format_optional_int(doc.get("rssi")),
                    "snr": _format_optional_float(doc.get("snr"), 2),
                    "timestamp": _format_timestamp(doc.get("timestamp")),
                    "sample_count": doc.get("sample_count"),
                }
            )

        return await self.templates.TemplateResponse(
            request,
            "sqladmin/telemetry_list.html",
            context={
                "title": "Telemetry",
                "subtitle": "MongoDB GPS and LoRa RF samples (read only)",
                "rows": rows,
                "total": total,
                "total_pages": total_pages,
                "filters": {
                    "company_id": company_id,
                    "cattle_id": cattle_id,
                    "source": source,
                    "page": page,
                    "page_size": page_size,
                },
            },
        )

    @staticmethod
    def _load_labels(
        documents: list[dict[str, Any]],
    ) -> tuple[dict[int, str], dict[int, str]]:
        company_ids = {
            int(doc["company_id"]) for doc in documents if doc.get("company_id")
        }
        cattle_ids = {
            int(doc["cattle_id"]) for doc in documents if doc.get("cattle_id")
        }
        if not company_ids and not cattle_ids:
            return {}, {}

        db = SessionFactory.create()
        try:
            company_names = {
                company.id: company.name
                for company in (
                    db.query(Company).filter(Company.id.in_(company_ids)).all()
                )
            }
            cattle_labels = {
                cattle.id: f"{cattle.tag} — {cattle.name}"
                for cattle in db.query(Cattle).filter(Cattle.id.in_(cattle_ids)).all()
            }
            return company_names, cattle_labels
        finally:
            db.close()
