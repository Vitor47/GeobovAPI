from app.adapters.container import container


def init_container(app):
    app.container = container
    container.wire(packages=["app.presentation.api.v1.endpoints"])
