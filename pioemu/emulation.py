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
from dataclasses import replace
from .state import State


def emulate(opcodes, *, initial_state=State(), max_clock_cycles=None):
    def run_conditions_met(state):
        return max_clock_cycles is None or state.clock < max_clock_cycles

    instruction_lookup = map_opcodes_to_callables()

    current_state = initial_state

    while run_conditions_met(current_state):
        previous_state = current_state

        opcode = opcodes[current_state.program_counter]
        data_field = opcode & 0x1F
        instruction = instruction_lookup.get(opcode & 0xE0E0, None)

        if instruction is not None:
            current_state = instruction(data_field, current_state)
            current_state = replace(current_state, clock=current_state.clock + 1)
            yield (previous_state, current_state)
        else:
            return (previous_state, None)


def next_instruction(state):
    return replace(state, program_counter=state.program_counter + 1)


def jmp_always(address, state):
    return replace(state, program_counter=address)


def set_pins(data, state):
    return next_instruction(replace(state, pin_values=data))


def set_pindirs(data, state):
    return next_instruction(replace(state, pin_directions=data))


def set_x(data, state):
    return next_instruction(replace(state, x_register=data))


def set_y(data, state):
    return next_instruction(replace(state, y_register=data))


def wait_for_gpio_low(pin_number, state):
    bit_mask = 1 << pin_number

    if not state.pin_values & bit_mask:
        return next_instruction(state)
    else:
        return state


def wait_for_gpio_high(pin_number, state):
    bit_mask = 1 << pin_number

    if state.pin_values & bit_mask:
        return next_instruction(state)
    else:
        return state


def map_opcodes_to_callables():
    return {
        0x0000: jmp_always,
        0x2020: wait_for_gpio_low,
        0x2080: wait_for_gpio_high,
        0xE080: set_pindirs,
        0xE000: set_pins,
        0xE020: set_x,
        0xE040: set_y,
    }
