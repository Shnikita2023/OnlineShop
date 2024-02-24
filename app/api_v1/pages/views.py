from starlette.templating import Jinja2Templates

templates: Jinja2Templates = Jinja2Templates(directory="app/api_v1/templates")


async def get_discount_page(products_discount: list[dict]) -> str:
    template = templates.get_template("discounts.html")
    return template.render(products_discount=products_discount)
