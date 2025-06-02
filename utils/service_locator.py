# utils/service_locator.py

from config.preference_manager import PreferenceManager # Import du nouveau gestionnaire de préférences

class ServiceLocator:
    _instance = None
    _services = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceLocator, cls).__new__(cls)
        return cls._instance

    def register_service(self, name, service_instance):
        """Registers a service instance with a given name."""
        self._services[name] = service_instance

    def get_service(self, name):
        """Retrieves a service instance by its name."""
        service = self._services.get(name)
        if service is None:
            raise ValueError(f"Service '{name}' not registered.")
        return service

    def clear_services(self):
        """Clears all registered services (useful for testing)."""
        self._services = {}

    def register_preferences(self, preference_manager_instance: PreferenceManager):
        """
        Registers the PreferenceManager instance.
        This provides centralized access to application settings.
        """
        self.register_service('preference_manager', preference_manager_instance)

# Instantiate the Service Locator once for the entire application
service_locator = ServiceLocator()