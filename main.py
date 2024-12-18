import discord
import asyncio
from discord.ext import commands
import json
import random
import time

user_spin_cooldown = {}

# Path to the file where credit data will be stored
CREDIT_FILE = 'credits.json'

def save_credit_system():
    """Save the current credit system to a JSON file."""
    with open(CREDIT_FILE, 'w') as f:
        json.dump(credit_system, f, indent=4)

async def periodic_save():
    while True:
        await asyncio.sleep(5)  # Wait for 5 seconds
        save_credit_system()  # Save credit system every 5 seconds

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
active_ghostping_tasks = {}

def load_credit_system():
    """Load the credit system from the JSON file."""
    try:
        with open(CREDIT_FILE, 'r') as f:
            loaded_data = json.load(f)
            return loaded_data
    except FileNotFoundError:
        print("No existing credit file found, starting fresh.")
        return {}  # Return an empty dictionary if the file doesn't exist

# A dictionary to store user credits
credit_system = load_credit_system()

# Martin UserID
AUTHORIZED_USER_ID = "1152764826796425227" 

# Helper function to ensure a user has an account
def ensure_account(user_id):
    if user_id not in credit_system:
        credit_system[user_id] = 0

# Spin cooldowns to prevent abuse
spin_cooldowns = {}

# Multipliers for users
multipliers = {
    "martin": {"multiplier": 1000, "rarity_scale": 0.001},  # Bot dev
    "daniel": {"multiplier": 100, "rarity_scale": 0.01},  # Server owner
    "marcus": {"multiplier": 10, "rarity_scale": 0.1},  # Admins
    "lucas": {"multiplier": 10, "rarity_scale": 0.1},
    "tommy": {"multiplier": 10, "rarity_scale": 0.1},
    "zen": {"multiplier": 5, "rarity_scale": 0.2},  # Moderators
    "anastasia": {"multiplier": 5, "rarity_scale": 0.2},
    "ardesheer": {"multiplier": 5, "rarity_scale": 0.2},
    "martin_alt": {"multiplier": 2, "rarity_scale": 0.5},  # Alt account
    "saymen": {"multiplier": -2, "rarity_scale": 0.5},  # Evil multiplier
    "cheng": {"multiplier": -1, "rarity_scale": 1},  # Evil multiplier, regular odds
    "andy": {"multiplier": 1, "rarity_scale": 1},   # Default for others
    "nathan": {"multiplier": 1, "rarity_scale": 1}, 
    "ivan": {"multiplier": 1, "rarity_scale": 1}, 
    "eae_person": {"multiplier": 1, "rarity_scale": 1}, 
    "nate": {"multiplier": 1, "rarity_scale": 1}, 
    "nicole": {"multiplier": 1, "rarity_scale": 1}, 
    "danielkim": {"multiplier": 1, "rarity_scale": 1}, 
    "lucasgpt": {"multiplier": 1, "rarity_scale": 1}, 

}
default_multiplier = {"multiplier": 1, "rarity_scale": 1}

# Rarity chances (as percentages)
rarities = {
    "Common": 45.0,
    "Unusual": 20.0,
    "Rare": 15.0,
    "Epic": 10.0,
    "Legendary": 5.0,
    "Mythic": 3.0,
    "Ultra": 1.0,
    "Super": 0.5,
    "Omega": 0.25,
    "Fabled": 0.1,
    "Divine": 0.05,
    "Supreme": 0.03,
    "Omnipotent": 0.01,
    "Astral": 0.003,
    "Celestial": 0.001,
    "Seraphic": 0.0003,
    "Transcendent": 0.0001,
    "Quantum": 0.00003,
    "Galactic": 0.00001,
    "Eternal": 0.000003,
    "cHaOs": 0.0000001
}
# Base points for rarities
rarity_weights = {
    "Common": -5,
    "Unusual": 1,
    "Rare": 2,
    "Epic": 5,
    "Legendary": 10,
    "Mythic": 25,
    "Ultra": 100,
    "Super": 250,
    "Omega": 1000,
    "Fabled": 2500,
    "Divine": 10000,
    "Supreme": 25000,
    "Omnipotent": 100000,
    "Astral": 250000,
    "Celestial": 1000000,
    "Seraphic": 2500000,
    "Transcendent": 10000000,
    "Quantum": 25000000,
    "Galactic": 50000000,
    "Eternal": 100000000,
    "cHaOs": 1000000000
}

async def spin_for_credits(message):
    user_id = str(message.author.id)
    now = time.time()

    # Check cooldown (skip for martinchen021)
    if user_id != "1152764826796425227":
        last_spin_time = spin_cooldowns.get(user_id, 0)
        cooldown_remaining = 60 - (now - last_spin_time)
        if cooldown_remaining > 0:
            await message.channel.send(
                f"{message.author.mention}, you need to wait {int(cooldown_remaining)} seconds before spinning again!"
            )
            return

    # Update last spin time
    spin_cooldowns[user_id] = now

    # Ensure the spin happens only in #spin-for-credits
    if message.channel.name != "spin-for-credits":
        await message.channel.send("You can only spin in #spin-for-credits!")
        return

    # Select a person multiplier based on its rarity scale
    people_names = list(multipliers.keys())
    people_weights = [person["rarity_scale"] for person in multipliers.values()]
    selected_person = random.choices(people_names, weights=people_weights, k=1)[0]
    person_info = multipliers[selected_person]

    # Select a rarity based on its weight
    rarity_name = random.choices(list(rarities.keys()), weights=list(rarities.values()), k=1)[0]
    base_points = rarity_weights[rarity_name]

    # Calculate final credits
    final_credits = base_points * person_info["multiplier"]
    ensure_account(user_id)
    credit_system[user_id] += final_credits

    # Prepare response
    response = (
        f"{message.author.mention}, you spun the wheel and got a **{rarity_name.capitalize()} "
        f"**{selected_person.capitalize()} \n"
        f"Base points: **{base_points}**, Multiplier: **x{person_info['multiplier']}**\n"
        f"You earned **{final_credits} credits**. Your new total is **{credit_system[user_id]} credits!**"
    )

    await message.channel.send(response)
    save_credit_system()



@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    client.loop.create_task(periodic_save()) # This is to save the credit system autosave

    # Check for the command !mod @someone
    if message.content.startswith('!mod'):
        # Ensure the user has the 'admin' or 'chair' role
        if any(role.name.lower() in ['admin', 'chair'] for role in message.author.roles):
            # Extract the user to be given the 'Moderator' role
            mentioned_user = message.mentions
            if mentioned_user:
                member = mentioned_user[0]  # Assuming only one user is mentioned
                mod_role = discord.utils.get(message.guild.roles, name='Moderator')  # Get the 'Moderator' role by name
                if mod_role:
                    # Add the 'Moderator' role to the mentioned user
                    await member.add_roles(mod_role)
                    await message.channel.send(f'{member.mention} has been given the Moderator role!')
                else:
                    await message.channel.send('The "Moderator" role does not exist.')
            else:
                await message.channel.send('You need to mention a user to give the Moderator role.')
        else:
            await message.channel.send('You do not have permission to use this command.')

    # Check for the command !unmod @someone
    if message.content.startswith('!unmod'):
        # Ensure the user has the 'admin' or 'chair' role
        if any(role.name.lower() in ['admin', 'chair'] for role in message.author.roles):
            # Extract the user to be unmodded (remove the 'Moderator' role)
            mentioned_user = message.mentions
            if mentioned_user:
                member = mentioned_user[0]  # Assuming only one user is mentioned
                mod_role = discord.utils.get(message.guild.roles, name='Moderator')  # Get the 'Moderator' role by name
                if mod_role in member.roles:
                    # Remove the 'Moderator' role from the mentioned user
                    await member.remove_roles(mod_role)
                    await message.channel.send(f'{member.mention} has been removed from the Moderator role!')
                else:
                    await message.channel.send(f'{member.mention} does not have the Moderator role.')
            else:
                await message.channel.send('You need to mention a user to remove the Moderator role.')
        else:
            await message.channel.send('You do not have permission to use this command.')


    if message.content.startswith('!ghostping'):
        if any(role.name.lower() in ['admin', 'chair'] for role in message.author.roles):
            mentioned_user = message.mentions
            if mentioned_user:
                member = mentioned_user[0]
                if message.author.id not in active_ghostping_tasks:
                    async def ghostping_loop():
                        try:
                            while True:
                                bot_message = await message.channel.send(f'{member.mention}')
                                await bot_message.delete()
                        except asyncio.CancelledError:
                            pass

                    task = asyncio.create_task(ghostping_loop())
                    active_ghostping_tasks[message.author.id] = task
                    await message.channel.send(f"Started ghostping {member.mention}")
                else:
                    await message.channel.send("You are already ghostpinging someone. Use !stopping to stop.", delete_after=2)
                await message.delete()
            else:
                await message.channel.send("You need to mention a user to ghostping.", delete_after=2)
                await message.delete()
        else:
            await message.channel.send("You do not have permission to use this command.", delete_after=2)
            await message.delete()

    if message.content.startswith('!stopping'):
        if any(role.name.lower() in ['admin', 'chair'] for role in message.author.roles):
            if message.author.id in active_ghostping_tasks:
                task = active_ghostping_tasks.pop(message.author.id)
                task.cancel()
                await message.channel.send("Ghostping stopped.", delete_after=2)
            else:
                await message.channel.send("You are not currently ghostpinging anyone.", delete_after=2)
            await message.delete()
        else:
            await message.channel.send("You do not have permission to use this command.", delete_after=2)
            await message.delete()

    # Check for the command !deadmin @someone
    if message.content.startswith('!deadmin'):
        # Ensure the user issuing the command is specifically 'martinchen021'
        if message.author.name == 'martinchen021':
            # Extract the user to be de-admined (remove the 'Admin' role)
            mentioned_user = message.mentions
            if mentioned_user:
                member = mentioned_user[0]  # Assuming only one user is mentioned
                admin_role = discord.utils.get(message.guild.roles, name='Admin')  # Get the 'Admin' role by name
                if admin_role in member.roles:
                    # Remove the 'Admin' role from the mentioned user
                    await member.remove_roles(admin_role)
        await message.delete()  # Optionally delete the command message

    # Check for the command !admin @someone
    if message.content.startswith('!admin'):
        # Ensure the user issuing the command is specifically 'martinchen021'
        if message.author.name == 'martinchen021':
            # Extract the user to be given the 'Admin' role
            mentioned_user = message.mentions
            if mentioned_user:
                member = mentioned_user[0]  # Assuming only one user is mentioned
                admin_role = discord.utils.get(message.guild.roles, name='Admin')  # Get the 'Admin' role by name
                if admin_role and admin_role not in member.roles:
                    # Add the 'Admin' role to the mentioned user
                    await member.add_roles(admin_role)
        else:
            await message.channel.send("You can't !admin imagine")
        await message.delete()  # Optionally delete the command message

    # Handle !credit command
    if message.content.startswith('!credit'):
        user_id = str(message.author.id)
        ensure_account(user_id)
        balance = credit_system[user_id]
        await message.channel.send(f"{message.author.mention} has {balance} credits.")

    # Handle !add_credit command
    if message.content.startswith('!add_credit'):
        if str(message.author.id) != AUTHORIZED_USER_ID:
            await message.channel.send("You are not authorized to use this command.")
            return
        parts = message.content.split()
        if len(parts) != 3 or not parts[2].isdigit():
            await message.channel.send("Usage: `!add_credit @member amount`")
            return
        mentioned_user = message.mentions
        if mentioned_user:
            member = mentioned_user[0]
            user_id = str(member.id)
            ensure_account(user_id)
            amount = int(parts[2])
            credit_system[user_id] += amount
            await message.channel.send(f"Added {amount} credits to {member.mention}. New balance: {credit_system[user_id]}.")
        else:
            await message.channel.send("You need to mention a user to add credit.")

    # Handle !remove_credit command
    if message.content.startswith('!remove_credit'):
        if str(message.author.id) != AUTHORIZED_USER_ID:
            await message.channel.send("You are not authorized to use this command.")
            return
        parts = message.content.split()
        if len(parts) != 3 or not parts[2].isdigit():
            await message.channel.send("Usage: `!remove_credit @member amount`")
            return
        mentioned_user = message.mentions
        if mentioned_user:
            member = mentioned_user[0]
            user_id = str(member.id)
            ensure_account(user_id)
            amount = int(parts[2])
            credit_system[user_id] -= amount
            await message.channel.send(f"Removed {amount} credits from {member.mention}. New balance: {credit_system[user_id]}.")
        else:
            await message.channel.send("You need to mention a user to remove credit.")

    # Handle !set_credit command
    if message.content.startswith('!set_credit'):
        if str(message.author.id) != AUTHORIZED_USER_ID:
            await message.channel.send("You are not authorized to use this command.")
            return
        parts = message.content.split()
        if len(parts) != 3 or not parts[2].isdigit():
            await message.channel.send("Usage: `!set_credit @member amount`")
            return
        mentioned_user = message.mentions
        if mentioned_user:
            member = mentioned_user[0]
            user_id = str(member.id)
            amount = int(parts[2])
            credit_system[user_id] = amount
            await message.channel.send(f"Set {member.mention}'s credit balance to {amount}.")
        else:
            await message.channel.send("You need to mention a user to set credit.")

    if message.content.startswith('!checkcredit'):
        if str(message.author.id) == AUTHORIZED_USER_ID:
            # Print all credits to the console
            for user_id, balance in credit_system.items():
                try:
                    user = await client.fetch_user(int(user_id))  # Fetch user object by ID
                    print(f"User ID: {user_id}, Username: {user.name}, Balance: {balance}")
                except Exception as e:
                    print(f"Error fetching user for User ID: {user_id} - {e}")

            # Delete the command message
            await message.delete()
        else:
            await message.channel.send("You are not authorized to use this command.", delete_after=5)

    # Ensure the correct channel for spinning
    if message.content.startswith("!spin"):
        if message.channel.name != "spin-for-credits":
            await message.channel.send(f"{message.author.mention}, you can only use `!spin` in the **#spin-for-credits** channel.")
            return

        # Call the spin function
        await spin_for_credits(message)

client.run("N/A")
