import logging
from typing import TYPE_CHECKING, Optional
from worlds.AutoWorld import World
from ..Helpers import clamp, get_items_with_value
from BaseClasses import MultiWorld, CollectionState

# from RulesExtension import disabled_items

import re

from worlds.generic.Rules import set_rule, add_rule
from Options import Choice, Toggle, Range, NamedRange

from ..Helpers import clamp, is_item_enabled, is_option_enabled, get_option_value, convert_string_to_type,\
    format_to_valid_identifier, format_state_prog_items_key, ProgItemsCat

if TYPE_CHECKING:
    from . import ManualWorld

classes = ["Scout", "Soldier", "Pyro", "Demoman", "Heavy", "Engineer", "Medic", "Sniper", "Spy"]

option_to_items: dict = {
    "GrappleKill": ["Grappling Hook"],
    "Mad Milk": ["Mad Milk"],
    "BannerAssists": ["Buff Banner", "Concheror", "Battalion's Backup"],
    "MantreadsKill": ["Mantreads"],
    "ThermalThrusterKill": ["Thermal Thruster"],
    "GasPasser": ["Gas Passer"],
    "MediGunChecks": ["Medi Gun","Kritzkrieg","Quick-Fix","Vaccinator"],
    "JarateAssist": ["Jarate"],
    "SapperDestructions": ["Sapper","Red-Tape Recorder"]
}

def disabled_items(multiworld: MultiWorld, player: int) -> list[str]:
    disabled: list[str] = []
    for option in option_to_items:
        if not is_option_enabled(multiworld, player, option):
            disabled.extend(option_to_items[option])
    return disabled

# # Sometimes you have a requirement that is just too messy or repetitive to write out with boolean logic.
# # Define a function here, and you can use it in a requires string with {function_name()}.
# def overfishedAnywhere(world: World, state: CollectionState, player: int):
#     """Has the player collected all fish from any fishing log?"""
#     for cat, items in world.item_name_groups:
#         if cat.endswith("Fishing Log") and state.has_all(items, player):
#             return True
#     return False

# # You can also pass an argument to your function, like {function_name(15)}
# # Note that all arguments are strings, so you'll need to convert them to ints if you want to do math.
# def anyClassLevel(state: CollectionState, player: int, level: str):
#     """Has the player reached the given level in any class?"""
#     for item in ["Figher Level", "Black Belt Level", "Thief Level", "Red Mage Level", "White Mage Level", "Black Mage Level"]:
#         if state.count(item, player) >= int(level):
#             return True
#     return False

# # You can also return a string from your function, and it will be evaluated as a requires string.
# def requiresMelee():
#     """Returns a requires string that checks if the player has unlocked the tank."""
#     return "|Figher Level:15| or |Black Belt Level:15| or |Thief Level:15|"

if TYPE_CHECKING:
    from __init__ import ManualWorld


# You can also pass an argument to your function, like {function_name(15)}
# Note that all arguments are strings, so you'll need to convert them to ints if you want to do math.
def GoalInLogic(world: "ManualWorld", multiworld: MultiWorld, state: CollectionState, player: int):
    possible_checks_by_class: dict = dict.fromkeys(classes, 0)
    possible_checks_by_class["Engineer"] = 1 #bc of sentry gun
    disabled: list[str] = disabled_items(multiworld, player)
    stocksanity: bool = is_option_enabled(multiworld, player, "Stocksanity")
    def has_item_for(name: str, location: dict):
        return (
            state.has(name, player) or
            state.has(name.split(" (")[0], player) or
            (stocksanity and "StockLocation" in location.get("category"))
        )
    for location in world.location_table:
        name: str = location.get("name", "Something that shouldn't have any matches")
        if location.get("victory", False) or name == "Grappling Hook":
            continue
        if has_item_for(name, location) and not name in disabled:
            for cat in location.get("category", []):
                for cla55 in classes:
                    if cla55 in cat:
                        possible_checks_by_class[cla55] += 1
        # raise Exception(f"""
        #     name: {str(name)}
        #     possible_checks_by_class: {str(possible_checks_by_class)}
        #     disabled: {str(disabled)}
        #     """)



    # for item in world.item_table:
    #     if item.get("category", [""])[0] == "Class Unlocks":
    #         class_unlocked[item.get("name", "")] = True
    #         continue
    #
    #     for key in classes:
    #         for category in item.get("category", []):
    #             if category.startswith(key) and item.get("progression", False):
    #                 for location in world.location_table:
    #                     if location.get("name", "").startswith(item.get("name", "-")):
    #                         possible_checks_by_class[key] += 1
    #                         break
    # items = state.prog_items[player]
    # raise Exception(f"""
    # possible_checks_by_class: {str(possible_checks_by_class)}
    # disabled: {str(disabled)}
    # """)
    unlock_classes: bool = is_option_enabled(multiworld, player, "UnlockClasses")
    for cla55 in classes:
        if (
            possible_checks_by_class[cla55] < get_option_value(multiworld, player, cla55) or
            (unlock_classes and not state.has(cla55, player))
        ):
            return False

    return True

