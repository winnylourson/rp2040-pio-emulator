# Copyright 2021 Nathan Young
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import pytest
from pioemu import emulate, State


def test_set_pins_directions():
    initial_state = State(pin_directions=0x1F)

    new_state = emulate_opcode(0xFF81, initial_state)  # set pindirs, 1 [31]

    assert new_state.pin_directions == 1


def test_set_pins_values():
    initial_state = State(pin_values=30)

    new_state = emulate_opcode(0xFF1F, initial_state)  # set pins, 31 [31]

    assert new_state.pin_values == 31


def test_set_x_register():
    initial_state = State(x_register=0)

    new_state = emulate_opcode(0xE03F, initial_state)  # set x, 31

    assert new_state.x_register == 31


def test_set_y_register():
    initial_state = State(y_register=0)

    new_state = emulate_opcode(0xE042, initial_state)  # set y, 2

    assert new_state.y_register == 2


@pytest.mark.parametrize(
    "opcode",
    [
        pytest.param(0xE03F, id="set x, 31"),
        pytest.param(0xE042, id="set y, 2"),
    ],
)
def test_set_consumes_one_clock_cycle(opcode):
    new_state = emulate_opcode(opcode, State())

    assert new_state.clock == 1


def emulate_opcode(opcode, initial_state):
    _, new_state = next(
        emulate([opcode], initial_state=initial_state, max_clock_cycles=1)
    )

    return new_state
