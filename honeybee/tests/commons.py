def create_url_from_parameters(base_url: str, parameters: dict) -> str:
    base_url = base_url.strip("/")

    parameter_strings = []
    for key, value in parameters.items():
        if isinstance(value, (list, tuple)):
            for v in value:
                parameter_strings.append(f"{key}={v}")
        else:
            parameter_strings.append(f"{key}={value}")

    parameters_string = "&".join(parameter_strings)

    return f"/{base_url}?{parameters_string}"
