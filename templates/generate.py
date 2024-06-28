import argparse
import base64
import os

from jinja2 import Environment
from jinja2 import FileSystemLoader

SOURCE = "apps"
GENERATED = "generated"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dev", action="store_true")
    parser.add_argument("-n", "--namespace", default="default")

    args = parser.parse_args()

    if args.dev:
        path = "apps-dev"
    else:
        path = GENERATED

    env = Environment(loader=FileSystemLoader(SOURCE))
    # list all yaml files in the apps folder
    for app in os.listdir(SOURCE):
        # 1. Load content of the yaml file
        # 2. Generate the template
        # 3. Save the generated file in the generated folder
        print(f"Generating {app}")
        ctx = {
            "namespace": args.namespace,
            "app_id": app[:-4],
            "user_id": "jankow",
            "mysql_root_password": base64.b64encode(b"password").decode(),
            "spot_pool": True,
            "proxy_domain": "apps.classlab.pl" if not args.dev else "apps.classlab.localhost",
        }

        if args.dev:
            ctx["spot_pool"] = False

        template = env.get_template(app)
        output = template.render(ctx)

        with open(f"{path}/{app}", "w") as f:
            f.write(output)


if __name__ == "__main__":
    main()
