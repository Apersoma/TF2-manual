
from worlds.AutoWorld import World
from BaseClasses import MultiWorld

from ..Helpers import is_option_enabled

option_to_items: dict = {
    "GrappleKill": ["Grappling Hook"],
    "Mad Milk": ["Mad Milk"],
    "BannerAssists": ["Buff Banner", "Concheror", "Battalion's Backup"],
    "MantreadsKill": ["Mantreads"],
    "ThermalThrusterKill": ["Thermal Thruster"],
    "GasPasser": ["Gas Passer"],
    "MediGunChecks": ["Medi Gun","Kritzkrieg","Quick-Fix","Vaccinator"],
    "JarateAssist": ["Jarate"],
    "SapperDestructions": ["Sapper""Red-Tape Recorder"]
}

def disabled_items(multiworld: MultiWorld, player: int) -> list[str]:
    disabled: list[str] = []
    for option in option_to_items:
        if not is_option_enabled(multiworld, player, option):
            disabled.extend(option_to_items[option])
    return disabled

# from typing import TYPE_CHECKING, Optional
# from enum import IntEnum
# from operator import eq, ge, le
#
# from ..Regions import regionMap
# import Rules
# from ..Helpers import clamp, is_item_enabled, is_option_enabled, get_option_value, convert_string_to_type,\
#     format_to_valid_identifier, format_state_prog_items_key, ProgItemsCat
#
# from BaseClasses import MultiWorld, CollectionState
# from worlds.AutoWorld import World
# from worlds.generic.Rules import set_rule, add_rule
# from Options import Choice, Toggle, Range, NamedRange
#
# import re
# import math
# import inspect
# import logging
#
#
# if TYPE_CHECKING:
#     from . import ManualWorld
#
# classes = ["Scout", "Soldier", "Pyro", "Demoman", "Heavy", "Engineer", "Medic", "Sniper", "Spy"]
#
# # You can also pass an argument to your function, like {function_name(15)}
# # Note that all arguments are strings, so you'll need to convert them to ints if you want to do math.
# def GoalInLogic(world: "ManualWorld", multiworld: MultiWorld, state: CollectionState, player: int):
#     possible_checks_by_class = dict.fromkeys(classes, 3)
#     possible_checks_by_class["Engineer"] = 4 #bc of sentry gun
#     possible_checks_by_class["Spy"] = 2 #bc of sapper
#
#     class_unlocked = dict.fromkeys(classes, False)
#     for item in world.item_table:
#         main_category = item.get("category", [""])[0]
#
#         if main_category == "Class Unlocks":
#             class_unlocked[item.get("name", "")] = True
#             continue
#
#         for key in classes:
#             if main_category.startswith(key) and item.get("progression", False):
#                 possible_checks_by_class[key] += state.count(item.get("name", ""), player)
#
#     required_kills = get_required_kills(multiworld, player)
#
#     for key in classes:
#         if possible_checks_by_class[key] < required_kills[key] or not class_unlocked[key]:
#             return False
#
#     return True
#
# def get_required_kills(multiworld: MultiWorld, player: int):
#     required_kills = dict.fromkeys(classes, 0)
#     for key in classes:
#         required_kills[key] = get_option_value(multiworld, player, "Required Kills")
#     # required_kills = get_option_value(multiworld, player, "Required Kills")
#     # if isinstance(required_kills, int):
#     #     required_kills = dict.fromkeys(classes, required_kills)
#     # elif "kills" in required_kills.keys():
#     #     required_kills = dict.fromkeys(classes, required_kills["kills"])
#     return required_kills
