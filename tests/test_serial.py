import pytest

import epson_projector

@pytest.fixture
async def projector(mock_serial):
    """Setup a serial projector."""

    # Mock responses needed to pass the initialization
    mock_serial.stub(
        receive_bytes=b"\r", send_bytes=b":"
    )
    mock_serial.stub(
        receive_bytes=b"PWR?\r", send_bytes=b"PWR=01\r:"
    )

    projector = epson_projector.Projector(
        host=mock_serial.port, type="serial"
    )

    yield projector

    projector.close()

async def test_get_property(projector, mock_serial):
    """Basic getting of a property."""

    power = await projector.get_property(epson_projector.const.POWER)
    assert power == "01"

    mock_serial.stub(
        receive_bytes=b"LAMP?\r", send_bytes=b"LAMP=12345\r:"
    )

    power = await projector.get_property("LAMP")
    assert power == "12345"

async def test_send_command(projector, mock_serial):

    mock_serial.stub(
        name="hdmi2",
        receive_bytes=b"KEY 40\r", send_bytes=b":"
    )

    await projector.send_command("HDMI2")

    assert mock_serial.stubs["hdmi2"].called
