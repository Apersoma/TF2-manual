# Object classes from AP core, to represent an entire MultiWorld and this individual World that's part of it
import random
from collections.abc import Sequence

from worlds.AutoWorld import World
from BaseClasses import MultiWorld, CollectionState, Item, ItemClassification

# Object classes from Manual -- extending AP core -- representing items and locations that are used in generation
from ..Items import ManualItem
from ..Locations import ManualLocation
from ..Helpers import clamp, is_item_enabled, is_option_enabled, get_option_value, convert_string_to_type,\
    format_to_valid_identifier, format_state_prog_items_key, ProgItemsCat
# Raw JSON data from the Manual apworld, respectively:
#          data/game.json, data/items.json, data/locations.json, data/regions.json
#
from ..Data import game_table, item_table, location_table, region_table

# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value, format_state_prog_items_key, ProgItemsCat

# calling logging.info("message") anywhere below in this file will output the message to both console and log file
import logging

option_to_items: dict = {
    "GrappleKill": ["Grappling Hook"],
    "MadMilkAssist": ["Mad Milk"],
    "BannerAssists": ["Buff Banner", "Concheror", "Battalion's Backup"],
    "MantreadsKill": ["Mantreads"],
    "ThermalThrusterKill": ["Thermal Thruster"],
    "GasPasser": ["Gas Passer"],
    "MediGunChecks": ["Medi Gun","Kritzkrieg","Quick-Fix","Vaccinator"],
    "JarateAssist": ["Jarate"],
    "SapperDestructions": ["Sapper""Red-Tape Recorder"]
}

classes = ("Scout", "Soldier", "Pyro", "Demoman", "Heavy", "Engineer", "Medic", "Sniper", "Spy")

def disabled_items(multiworld: MultiWorld, player: int) -> list[str]:
    disabled: list[str] = []
    for option in option_to_items:
        if not is_option_enabled(multiworld, player, option):
            disabled.extend(option_to_items[option])
    return disabled

def get_name(item) -> str:
    if isinstance(item, str):
        return item
    else:
        return str(getattr(item, "name"))

def to_table_item(item) -> dict:
    name: str = get_name(item)

    for tbl_item in item_table:
        if tbl_item.name == name:
            return tbl_item

    raise Exception(f"Could not find an item with the name: \"{name}\". Parameter 'item' was {item}.")

def to_item(item, item_pool: list, player: int):
    name: str = get_name(item)

    for pool_item in item_pool:
        if pool_item.player == player and pool_item.name == name:
            return pool_item

    raise Exception(f"Could not find an item with the name: \"{name}\". Parameter 'item' was {item}.")

def to_items(items: list, item_pool: list, player: int) -> list:
    out = list()
    for item in items:
        out.append(to_item(item, item_pool, player))
    return out

def get_category(item) -> list[str]:
    if hasattr(item, "category"):
        category = getattr(item, "category")
        if isinstance(category, list) and (len(category) == 0 or isinstance(category[0], str)):
            return category
    return to_table_item(item).get("category", [])

class ItemsByCategorySubstring(dict):
    def __init__(
            self,
            item_pool: list,
            keys: Sequence[str] = classes,
            convert_to_table_items: bool = False,
            convert_to_item_names: bool = False,
            convert_to_item_table_item_tuple: bool = False,
            item_is_not_key: bool = False,
            player: int | None = None
    ):
        dict.__init__(dict.fromkeys(classes, []))

        def add(key: str, item):
            if convert_to_table_items:
                self[key].append(to_table_item(item))
            elif convert_to_item_names:
                self[key].append(get_name(item))
            elif convert_to_item_table_item_tuple:
                self[key].append((item, to_table_item(item)))
            else:
                self[key].append(item)


        for item in item_pool:
            if player is not None and item.player != player:
                continue
            if item_is_not_key and get_name(item) in keys:
                continue
            for cat in get_category(item):
                for key in keys:
                    if key in cat:
                        add(key, item)







########################################################################################
## Order of method calls when the world generates:
##    1. create_regions - Creates regions and locations
##    2. create_items - Creates the item pool
##    3. set_rules - Creates rules for accessing regions and locations
##    4. generate_basic - Runs any post item pool options, like place item/category
##    5. pre_fill - Creates the victory location
##
## The create_item method is used by plando and start_inventory settings to create an item from an item name.
## The fill_slot_data method will be used to send data to the Manual client for later use, like deathlink.
########################################################################################



# Use this function to change the valid filler items to be created to replace item links or starting items.
# Default value is the `filler_item_name` from game.json
def hook_get_filler_item_name(world: World, multiworld: MultiWorld, player: int) -> str | bool:
    return False

# Called before regions and locations are created. Not clear why you'd want this, but it's here. Victory location is included, but Victory event is not placed yet.
def before_create_regions(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after regions and locations are created, in case you want to see or modify that information. Victory location is included.
def after_create_regions(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to remove locations from the world
    locationNamesToRemove: list[str] = [] # List of location names

    # Add your code here to calculate which locations to remove

    for region in multiworld.regions:
        if region.player == player:
            for location in list(region.locations):
                if location.name in locationNamesToRemove:
                    region.locations.remove(location)

# This hook allows you to access the item names & counts before the items are created. Use this to increase/decrease the amount of a specific item in the pool
# Valid item_config key/values:
# {"Item Name": 5} <- This will create qty 5 items using all the default settings
# {"Item Name": {"useful": 7}} <- This will create qty 7 items and force them to be classified as useful
# {"Item Name": {"progression": 2, "useful": 1}} <- This will create 3 items, with 2 classified as progression and 1 as useful
# {"Item Name": {0b0110: 5}} <- If you know the special flag for the item classes, you can also define non-standard options. This setup
#       will create 5 items that are the "useful trap" class
# {"Item Name": {ItemClassification.useful: 5}} <- You can also use the classification directly
def before_create_items_all(item_config: dict[str, int|dict], world: World, multiworld: MultiWorld, player: int) -> dict[str, int|dict]:
    return item_config

# The item pool before starting items are processed, in case you want to see the raw item pool at that stage
def before_create_items_starting(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    mark_non_progression: list[str] = disabled_items(multiworld, player)

    for item in item_pool:
        if item.player != player:
            continue
        if item.name in mark_non_progression:
            if (
                    item.name == "Gas Passer" or item.name == "Red-Tape Recorder"
            ):
                item.classification = ItemClassification.filler
            else:
                item.classification = ItemClassification.useful

    local_items: list[tuple] = list()
    for item in item_pool:
        if item.player == player:
            local_items.append((item, to_table_item(item)))


    class_count = get_option_value(multiworld, player, "StartingClassCount")
    class_weapon_count = get_option_value(multiworld, player, "StartingClassWeaponCount")
    class_item_count = get_option_value(multiworld, player, "StartingClassItemCount")
    item_count = get_option_value(multiworld, player, "StartingItemCount")
    weapon_count = get_option_value(multiworld, player, "StartingWeaponCount")

    if class_count == 0:
        return item_pool

    starting_classes = list(classes)
    random.seed(multiworld.seed)
    random.shuffle(starting_classes)
    starting_classes = starting_classes[:class_count]

    class_weapons = list()
    class_items = list()
    weapons = list()

    for item, tbl_item in local_items:
        if item.name in starting_classes:
            multiworld.push_precollected(item)
            item_pool.remove(item)
        else:
            category = tbl_item.get("category", [])
            if "Class Unlock" in category:
                continue


            weapon: bool = bool(item.classification & ItemClassification.progression)

            if weapon and weapon_count:
                weapons.append(item)

            for cat in category:
                for starting_class in starting_classes:
                    if starting_class in cat:
                        if class_item_count:
                            class_items.append(item)
                        if class_weapon_count and weapon:
                            class_weapons.append(item)
                        break
                else:
                    continue
                break

    if class_weapon_count:
        random.shuffle(class_weapons)
        for item in class_weapons[:class_weapon_count]:
            multiworld.push_precollected(item)
            item_pool.remove(item)
            local_items.remove(item)
            class_items.remove(item)
            weapons.remove(item)

    if class_item_count:
        random.shuffle(class_items)
        for item in class_items[:class_item_count]:
            multiworld.push_precollected(item)
            item_pool.remove(item)
            local_items.remove(item)
            try:
                weapons.remove(item)
            except ValueError:
                continue

    if weapon_count:
        random.shuffle(weapons)
        for item in weapons[:weapon_count]:
            multiworld.push_precollected(item)
            item_pool.remove(item)
            local_items.remove(item)

    if item_count:
        random.shuffle(local_items)
        for item in local_items[:item_count]:
            multiworld.push_precollected(item)
            item_pool.remove(item)
            local_items.remove(item)

    return item_pool

# The item pool after starting items are processed but before filler is added, in case you want to see the raw item pool at that stage
def before_create_items_filler(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    # Use this hook to remove items from the item pool
    itemNamesToRemove: list[str] = [] # List of item names

    # Add your code here to calculate which items to remove.
    #
    # Because multiple copies of an item can exist, you need to add an item name
    # to the list multiple times if you want to remove multiple copies of it.

    for itemName in itemNamesToRemove:
        item = next(i for i in item_pool if i.name == itemName)
        item_pool.remove(item)
    return item_pool



    # Some other useful hook options:

    ## Place an item at a specific location
    # location = next(l for l in multiworld.get_unfilled_locations(player=player) if l.name == "Location Name")
    # item_to_place = next(i for i in item_pool if i.name == "Item Name")
    # location.place_locked_item(item_to_place)
    # item_pool.remove(item_to_place)

# option_to_items: dict = {
#     "GrappleKill": ["Grappling Hook"],
#     "Mad Milk": ["Mad Milk"],
#     "BannerAssists": ["Buff Banner", "Concheror", "Battalion's Backup"],
#     "MantreadsKill": ["Mantreads"],
#     "ThermalThrusterKill": ["Thermal Thruster"],
#     "GasPasser": ["Gas Passer"],
#     "MediGunChecks": ["Medi Gun","Kritzkrieg","Quick-Fix","Vaccinator"],
#     "JarateAssist": ["Jarate"],
#     "SapperDestructions": ["Sapper""Red-Tape Recorder"]
# }
#
# def disabled_items(multiworld: MultiWorld, player: int) -> list[str]:
#     disabled: list[str] = []
#     for option in option_to_items:
#         if not is_option_enabled(multiworld, player, option):
#             disabled.extend(option_to_items[option])
#     return disabled

# The complete item pool prior to being set for generation is provided here, in case you want to make changes to it
def after_create_items(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    "was the following, the following was moved to before_create_items_starting"
    # mark_non_progression: list[str] = disabled_items(multiworld, player)
    #
    # for item in item_pool:
    #     if item.name in mark_non_progression:
    #         if (
    #             item.name == "Gas Passer" or item.name == "Red-Tape Recorder"
    #         ):
    #             item.classification = ItemClassification.filler
    #         else:
    #             item.classification = ItemClassification.useful
    #
    #
    # return item_pool
    return item_pool

# Called before rules   for accessing regions and locations are created. Not clear why you'd want this, but it's here.
def before_set_rules(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after rules for accessing regions and locations are created, in case you want to see or modify that information.
def after_set_rules(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to modify the access rules for a given location

    def Example_Rule(state: CollectionState) -> bool:
        # Calculated rules take a CollectionState object and return a boolean
        # True if the player can access the location
        # CollectionState is defined in BaseClasses
        return True

    ## Common functions:
    # location = world.get_location(location_name, player)
    # location.access_rule = Example_Rule

    ## Combine rules:
    # old_rule = location.access_rule
    # location.access_rule = lambda state: old_rule(state) and Example_Rule(state)
    # OR
    # location.access_rule = lambda state: old_rule(state) or Example_Rule(state)

# The item name to create is provided before the item is created, in case you want to make changes to it
def before_create_item(item_name: str, world: World, multiworld: MultiWorld, player: int) -> str:
    return item_name

# The item that was created is provided after creation, in case you want to modify the item
def after_create_item(item: ManualItem, world: World, multiworld: MultiWorld, player: int) -> ManualItem:
    return item

# This method is run towards the end of pre-generation, before the place_item options have been handled and before AP generation occurs
def before_generate_basic(world: World, multiworld: MultiWorld, player: int):
    pass

# This method is run at the very end of pre-generation, once the place_item options have been handled and before AP generation occurs
def after_generate_basic(world: World, multiworld: MultiWorld, player: int):
    pass

# This method is run every time an item is added to the state, can be used to modify the value of an item.
# IMPORTANT! Any changes made in this hook must be cancelled/undone in after_remove_item
def after_collect_item(world: World, state: CollectionState, Changed: bool, item: Item):
    # the following let you add to the Potato Item Value count
    # if item.name == "Cooked Potato":
    #     state.prog_items[item.player][format_state_prog_items_key(ProgItemsCat.VALUE, "Potato")] += 1
    pass

# This method is run every time an item is removed from the state, can be used to modify the value of an item.
# IMPORTANT! Any changes made in this hook must be first done in after_collect_item
def after_remove_item(world: World, state: CollectionState, Changed: bool, item: Item):
    # the following let you undo the addition to the Potato Item Value count
    # if item.name == "Cooked Potato":
    #     state.prog_items[item.player][format_state_prog_items_key(ProgItemsCat.VALUE, "Potato")] -= 1
    pass


# This is called before slot data is set and provides an empty dict ({}), in case you want to modify it before Manual does
def before_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data

# This is called after slot data is set and provides the slot data at the time, in case you want to check and modify it after Manual is done with it
def after_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data

# This is called right at the end, in case you want to write stuff to the spoiler log
def before_write_spoiler(world: World, multiworld: MultiWorld, spoiler_handle) -> None:
    pass

# This is called when you want to add information to the hint text
def before_extend_hint_information(hint_data: dict[int, dict[int, str]], world: World, multiworld: MultiWorld, player: int) -> None:

    ### Example way to use this hook:
    # if player not in hint_data:
    #     hint_data.update({player: {}})
    # for location in multiworld.get_locations(player):
    #     if not location.address:
    #         continue
    #
    #     use this section to calculate the hint string
    #
    #     hint_data[player][location.address] = hint_string

    pass

def after_extend_hint_information(hint_data: dict[int, dict[int, str]], world: World, multiworld: MultiWorld, player: int) -> None:
    pass
