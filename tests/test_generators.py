"""Test generator modules."""


def test_model_generator_import():
    """Test model generator can be imported."""
    from lazydjango.generators import model_gen

    assert model_gen is not None


def test_view_generator_import():
    """Test view generator can be imported."""
    from lazydjango.generators import view_gen

    assert view_gen is not None


def test_admin_generator_import():
    """Test admin generator can be imported."""
    from lazydjango.generators import admin_gen

    assert admin_gen is not None


def test_auth_generator_import():
    """Test auth generator can be imported."""
    from lazydjango.generators import auth_gen

    assert auth_gen is not None
