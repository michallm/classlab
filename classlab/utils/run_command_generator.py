from django.template import Context
from django.template import Template


class RunCommandGenerator:
    def __init__(self, template: str, config: dict):
        self.template = template
        self.config = config

    def generate(self) -> str:
        ctx = Context(self.config)
        template = Template(self.template)
        return template.render(ctx)
