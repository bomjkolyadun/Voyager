import importlib.resources
import os
import voyager.utils as U


def load_control_primitives_context(primitive_names=None):
    # Using importlib.resources with files() method for directory access
    try:
        context_path = importlib.resources.files("voyager") / "control_primitives_context"
        if primitive_names is None:
            primitive_names = [
                f.name[:-3]
                for f in context_path.iterdir()
                if f.name.endswith(".js")
            ]
        primitives = []
        for primitive_name in primitive_names:
            content = (context_path / f"{primitive_name}.js").read_text()
            primitives.append(content)
        return primitives
    except (AttributeError, TypeError):
        # Fallback for older Python versions
        import pkg_resources
        package_path = pkg_resources.resource_filename("voyager", "")
        if primitive_names is None:
            primitive_names = [
                primitive[:-3]
                for primitive in os.listdir(f"{package_path}/control_primitives_context")
                if primitive.endswith(".js")
            ]
        primitives = [
            U.load_text(f"{package_path}/control_primitives_context/{primitive_name}.js")
            for primitive_name in primitive_names
        ]
        return primitives
