get_functions = {}
post_functions = {}
update_functions = {}
delete_functions = {}

VALID_METHODS = ["GET", "POST", "UPDATE", "DELETE"]

def http_method_decorator(method, functions_dict):
    def decorator(key, param_types={}):
        def wrapper(func):
            def inner_wrapper(*args, **kwargs):
                # Check parameter types
                for param, param_type in param_types.items():
                    if param in kwargs and not isinstance(kwargs[param], param_type):
                        raise TypeError(f"Invalid type for parameter '{param}'. Expected {param_type.__name__}, got {type(kwargs[param]).__name__}")

                # Execute the wrapped function
                result = func(*args, **kwargs)

                # Return the result of the wrapped function
                return result


            functions_dict[key] = inner_wrapper
            return inner_wrapper

        return wrapper

    return decorator

def get(key, param_types={}):
    return http_method_decorator("GET", get_functions)(key, param_types)

def post(key, param_types={}):
    return http_method_decorator("POST", post_functions)(key, param_types)

def update(key, param_types={}):
    return http_method_decorator("UPDATE", update_functions)(key, param_types)

def delete(key, param_types={}):
    return http_method_decorator("DELETE", delete_functions)(key, param_types)
