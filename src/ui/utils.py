import datetime
from typing import Any

from fastapi.templating import Jinja2Templates

TEMPLATE_GLOBALS = {
    "now": datetime.datetime.utcnow,
}


class TemplateResponseWithGlobals(Jinja2Templates):
    """
    A custom Jinja2Templates class that automatically injects global context
    into every template response.
    """

    def TemplateResponse(
        self,
        name: str,
        context: dict[str, Any],
        *args,
        **kwargs,
    ):
        full_context = TEMPLATE_GLOBALS.copy()
        full_context.update(context)

        return super().TemplateResponse(name, full_context, *args, **kwargs)


templates = TemplateResponseWithGlobals(directory="src/ui/templates")
