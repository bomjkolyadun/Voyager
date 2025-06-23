import importlib.resources
import os
import voyager.utils as U


def load_control_primitives(primitive_names=None):
    # Using importlib.resources with files() method for directory access
    try:
        primitives_path = importlib.resources.files("voyager") / "control_primitives"
        if primitive_names is None:
            primitive_names = [
                f.name[:-3]
                for f in primitives_path.iterdir()
                if f.name.endswith(".js")
            ]
        primitives = []
        for primitive_name in primitive_names:
            content = (primitives_path / f"{primitive_name}.js").read_text()
            primitives.append(content)
        return primitives
    except (AttributeError, TypeError):
        # Fallback for older Python versions
        import pkg_resources
        package_path = pkg_resources.resource_filename("voyager", "")
        if primitive_names is None:
            primitive_names = [
                primitives[:-3]
                for primitives in os.listdir(f"{package_path}/control_primitives")
                if primitives.endswith(".js")
            ]
        primitives = [
            U.load_text(f"{package_path}/control_primitives/{primitive_name}.js")
            for primitive_name in primitive_names
        ]
        return primitives
