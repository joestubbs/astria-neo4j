import yaml
from openapi_spec_validator import validate_spec
from openapi_spec_validator.readers import read_from_filename

# Load YAML file
spec_dict, spec_url = read_from_filename("openapi.yaml")

# Validate
errors = validate_spec(spec_dict)

if errors is None:
    print("✅ OpenAPI definition is valid!")
else:
    print("❌ Errors found:", errors)
