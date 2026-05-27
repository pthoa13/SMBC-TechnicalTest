from brightlearn_site.site.renderer import create_template_environment


def test_template_environment_loads_base_template() -> None:
    env = create_template_environment()

    assert env.get_template("base.html")
