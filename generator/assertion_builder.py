def build_assertions(response_fields):

   

    assertions = []

    type_map = {
        "int": "int",
        "string": "str",
        "float": "float",
        "bool": "bool"
    }

    for field_name, field_type in response_fields.items():

        py_type = type_map.get(field_type, "str")

        lines = []

        # 类型检查
        lines.append(
            f'assert isinstance(response_data["{field_name}"], {py_type})'
        )

        # string 非空
        if field_type == "string":

            lines.append(
                f'assert response_data["{field_name}"] != ""'
            )

        # int >= 0
        if field_type == "int":

            lines.append(
                f'assert response_data["{field_name}"] >= 0'
            )

        # 把所有检查包进 if 里
        block = (
            f'if "{field_name}" in case["expected_fields"]:\n'
            + "\n".join(f"    {line}" for line in lines)
        )

        assertions.append(block)

    return "\n\n".join(assertions)