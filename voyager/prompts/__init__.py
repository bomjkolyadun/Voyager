import importlib.resources
import voyager.utils as U


def load_prompt(prompt):
    # Using importlib.resources with files() method
    try:
        prompts_path = importlib.resources.files("voyager") / "prompts"
        content = (prompts_path / f"{prompt}.txt").read_text()
        return content
    except (AttributeError, TypeError):
        # Fallback for older Python versions
        import pkg_resources
        package_path = pkg_resources.resource_filename("voyager", "")
        return U.load_text(f"{package_path}/prompts/{prompt}.txt")
