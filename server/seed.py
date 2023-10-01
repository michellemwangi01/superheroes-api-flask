from app import  app
from models import Power, Hero, HeroPower, db
import random

with app.app_context():
    Hero.query.delete()
    Power.query.delete()
    HeroPower.query.delete()

    print("🦸‍♀️ Seeding powers...")

    powers_data = [
        {"name": "super strength", "description": "gives the wielder super-human strengths"},
        {"name": "flight", "description": "gives the wielder the ability to fly through the skies at supersonic speed"},
        {"name": "super human senses", "description": "allows the wielder to use her senses at a super-human level"},
        {"name": "elasticity", "description": "can stretch the human body to extreme lengths"}
    ]

    for data in powers_data:
        power = Power(**data)
        db.session.add(power)

    db.session.commit()

    print("🦸‍♀️ Seeding heroes...")

    heroes_data = [
        {"name": "Kamala Khan", "super_name": "Ms. Marvel"},
        {"name": "Doreen Green", "super_name": "Squirrel Girl"},
        {"name": "Gwen Stacy", "super_name": "Spider-Gwen"},
        {"name": "Janet Van Dyne", "super_name": "The Wasp"},
        {"name": "Wanda Maximoff", "super_name": "Scarlet Witch"},
        {"name": "Carol Danvers", "super_name": "Captain Marvel"},
        {"name": "Jean Grey", "super_name": "Dark Phoenix"},
        {"name": "Ororo Munroe", "super_name": "Storm"},
        {"name": "Kitty Pryde", "super_name": "Shadowcat"},
        {"name": "Elektra Natchios", "super_name": "Elektra"}
    ]

    for data in heroes_data:
        hero = Hero(**data)
        db.session.add(hero)

    db.session.commit()

    print("🦸‍♀️ Adding powers to heroes...")

    strengths = ["Strong", "Weak", "Average"]

    heroes = Hero.query.all()
    powers = Power.query.all()

    for hero in heroes:
        for _ in range(random.randint(1, 3)):
            power = random.choice(powers)
            strength = random.choice(strengths)

            hero_power = HeroPower(hero_id=hero.id, power_id=power.id, strength=strength)
            db.session.add(hero_power)
            print(hero_power)

    db.session.commit()

    print("🦸‍♀️ Done seeding!")
