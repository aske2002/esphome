from collections.abc import Callable
from contextlib import AbstractContextManager
from dataclasses import dataclass
import importlib
import importlib.abc
import importlib.resources
import importlib.util
import logging
from pathlib import Path
import sys
from types import ModuleType
from typing import Any

from esphome.const import SOURCE_FILE_EXTENSIONS
from esphome.core import CORE
import esphome.core.config
from esphome.types import ConfigType

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, order=True)
class FileResource:
    package: str
    resource: str

    def path(self) -> AbstractContextManager[Path]:
        return importlib.resources.as_file(
            importlib.resources.files(self.package) / self.resource
        )


class ComponentManifest:
    def __init__(self, module: ModuleType):
        self.module = module

    @property
    def package(self) -> str:
        """Return the package name the module is contained in.

        Examples:
        - esphome/components/gpio/__init__.py -> esphome.components.gpio
        - esphome/components/gpio/switch/__init__.py -> esphome.components.gpio.switch
        - esphome/components/a4988/stepper.py -> esphome.components.a4988
        """
        return self.module.__package__

    @property
    def is_platform(self) -> bool:
        return len(self.module.__name__.split(".")) == 4

    @property
    def is_platform_component(self) -> bool:
        return getattr(self.module, "IS_PLATFORM_COMPONENT", False)

    @property
    def is_target_platform(self) -> bool:
        return getattr(self.module, "IS_TARGET_PLATFORM", False)

    @property
    def config_schema(self) -> Any | None:
        return getattr(self.module, "CONFIG_SCHEMA", None)

    @property
    def multi_conf(self) -> bool:
        return getattr(self.module, "MULTI_CONF", False)

    @property
    def multi_conf_no_default(self) -> bool:
        return getattr(self.module, "MULTI_CONF_NO_DEFAULT", False)

    @property
    def to_code(self) -> Callable[[Any], None] | None:
        return getattr(self.module, "to_code", None)

    @property
    def dependencies(self) -> list[str]:
        return getattr(self.module, "DEPENDENCIES", [])

    @property
    def conflicts_with(self) -> list[str]:
        return getattr(self.module, "CONFLICTS_WITH", [])

    @property
    def auto_load(self) -> list[str]:
        al = getattr(self.module, "AUTO_LOAD", [])
        if callable(al):
            return al()
        return al

    @property
    def codeowners(self) -> list[str]:
        return getattr(self.module, "CODEOWNERS", [])

    @property
    def instance_type(self) -> list[str]:
        return getattr(self.module, "INSTANCE_TYPE", None)

    @property
    def final_validate_schema(self) -> Callable[[ConfigType], None] | None:
        """Components can declare a `FINAL_VALIDATE_SCHEMA` cv.Schema that gets called
        after the main validation. In that function checks across components can be made.

        Note that the function can't mutate the configuration - no changes are saved
        """
        return getattr(self.module, "FINAL_VALIDATE_SCHEMA", None)

    @property
    def resources(self) -> list[FileResource]:
        """Return a list of all file resources defined in the package of this component.

        This will return all cpp source files that are located in the same folder as the
        loaded .py file (does not look through subdirectories)
        """
        ret = []

        for resource in (
            r.name
            for r in importlib.resources.files(self.package).iterdir()
            if r.is_file()
        ):
            if Path(resource).suffix not in SOURCE_FILE_EXTENSIONS:
                continue
            if not importlib.resources.files(self.package).joinpath(resource).is_file():
                # Not a resource = this is a directory (yeah this is confusing)
                continue
            ret.append(FileResource(self.package, resource))
        return ret


class ComponentMetaFinder(importlib.abc.MetaPathFinder):
    def __init__(
        self, components_path: Path, allowed_components: list[str] | None = None
    ) -> None:
        self._allowed_components = allowed_components
        self._finders = []
        for hook in sys.path_hooks:
            try:
                finder = hook(str(components_path))
            except ImportError:
                continue
            self._finders.append(finder)

    def find_spec(self, fullname: str, path: list[str] | None, target=None):
        if not fullname.startswith("esphome.components."):
            return None
        parts = fullname.split(".")
        if len(parts) != 3:
            # only handle direct components, not platforms
            # platforms are handled automatically when parent is imported
            return None
        component = parts[2]
        if (
            self._allowed_components is not None
            and component not in self._allowed_components
        ):
            return None

        for finder in self._finders:
            spec = finder.find_spec(fullname, target=target)
            if spec is not None:
                return spec
        return None


def clear_component_meta_finders():
    sys.meta_path = [x for x in sys.meta_path if not isinstance(x, ComponentMetaFinder)]


def install_meta_finder(
    components_path: Path, allowed_components: list[str] | None = None
):
    sys.meta_path.insert(0, ComponentMetaFinder(components_path, allowed_components))


def install_custom_components_meta_finder():
    custom_components_dir = (Path(CORE.config_dir) / "custom_components").resolve()
    install_meta_finder(custom_components_dir)


def _lookup_module(domain, exception):
    if domain in _COMPONENT_CACHE:
        return _COMPONENT_CACHE[domain]

    try:
        module = importlib.import_module(f"esphome.components.{domain}")
    except ImportError as e:
        if exception:
            raise
        if "No module named" in str(e):
            _LOGGER.info(
                "Unable to import component %s: %s", domain, str(e), exc_info=False
            )
        else:
            _LOGGER.error("Unable to import component %s:", domain, exc_info=True)
        return None
    except Exception:  # pylint: disable=broad-except
        if exception:
            raise
        _LOGGER.error("Unable to load component %s:", domain, exc_info=True)
        return None

    manif = ComponentManifest(module)
    _COMPONENT_CACHE[domain] = manif
    return manif


def get_component(domain, exception=False):
    assert "." not in domain
    return _lookup_module(domain, exception)


def get_platform(domain, platform):
    full = f"{platform}.{domain}"
    return _lookup_module(full, False)


_COMPONENT_CACHE = {}
CORE_COMPONENTS_PATH = (Path(__file__).parent / "components").resolve()
_COMPONENT_CACHE["esphome"] = ComponentManifest(esphome.core.config)
