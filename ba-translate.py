#!/usr/bin/env python3
import json, os, textwrap, re

###==============================================
### Helper functions
def toEnumStr(string: str):
    return re.sub(r'([a-z](?=[A-Z])|[A-Z](?=[A-Z][a-z]))', r'\1_', string).lower()

def stripName(string: str):
    string = string.replace("_default", "")
    string = string.replace("_", " ")

    wrongNames = [
        ("Aris", "Alice"),
        ("Hihumi", "Hifumi"),
        ("Zunko", "Junko")
    ]
    for wrongName in wrongNames:
        string = string.replace(wrongName[0], wrongName[1])
    
    return string

###==============================================
### Schemes
def toZZZString(student):
    result = textwrap.dedent(f"""\
    id: {student["Id"]}
    dev name: {student["DevName"]}
    production step: {student["ProductionStep"]} 


    ### ------- INFO -------
    name: {student["StrippedName"]}
    rarity: {student["Rarity"]}{(" : " + '★'*student["DefaultStarGrade"] + '☆'*(student["MaxStarGrade"] - student["DefaultStarGrade"])) if student["MaxStarGrade"] > 0 else ""}

    school: {student["School"]}
    club: "{student["Club"]}"
    tags: {" :; ".join('"{}"'.format(tag) for tag in student["Tags"]) if len(student["Tags"]) > 0 else '""'}


    ### ------- STATUS -------
    type: {"striker" if student["SquadType"] == "Main" else "special" if student["SquadType"] == "Support" else student["SquadType"].lower()}
    role: {toEnumStr(student["TacticRole"])}
    position: {toEnumStr(student["TacticRange"])}

    armor: {toEnumStr(student["ArmorType"])}
    bullet: {toEnumStr(student["BulletType"])}

    weapon: {student["WeaponType"] if student["WeaponType"].isupper() else toEnumStr(student["WeaponType"])}
    aim ik: {toEnumStr(student["AimIKType"])}

    equipments: {" :; ".join([equipment.lower() for equipment in student["EquipmentSlot"]]) if len(student["EquipmentSlot"]) > 0 else "null"}
    """)

    if "stat" in student.keys():
        result = result + textwrap.dedent(f"""

        ### ------- STATS -------
        hp:
          min: {student["stat"]["MaxHP1"]}
          max: {student["stat"]["MaxHP100"]}
        atk:
          min: {student["stat"]["AttackPower1"]}
          max: {student["stat"]["AttackPower100"]}
        def:
          min: {student["stat"]["DefensePower1"]}
          max: {student["stat"]["DefensePower100"]}
        heal:
          min: {student["stat"]["HealPower1"]}
          max: {student["stat"]["HealPower100"]}

        stability:
          rate: {student["stat"]["StabilityRate"]} : {student["stat"]["StabilityRate"] / 100:.0f}%
          point: {student["stat"]["StabilityPoint"]}

        critical:
          crit point: {student["stat"]["CriticalPoint"]}
          crit dmg rate: {student["stat"]["CriticalDamageRate"]} : {student["stat"]["CriticalDamageRate"] / 100:.0f}%

          res point: {student["stat"]["CriticalResistPoint"]}
          res dmg rate: {student["stat"]["CriticalDamageResistRate"]} : {student["stat"]["CriticalDamageResistRate"] / 100:.0f}%

        oppression:
          power: {student["stat"]["OppressionPower"]}
          resist: {student["stat"]["OppressionResist"]}

        ammo:
          cost: {student["stat"]["AmmoCost"]}
          count: {student["stat"]["AmmoCount"]}

        range: {student["stat"]["Range"]}
        regen: {student["stat"]["RegenCost"]}
        dodge: {student["stat"]["DodgePoint"]}
        accuracy: {student["stat"]["AccuracyPoint"]}

        environment:
          street: {student["stat"]["StreetBattleAdaptation"]}
          indoor: {student["stat"]["IndoorBattleAdaptation"]}
          outdoor: {student["stat"]["OutdoorBattleAdaptation"]}
        """)
    
    if "profile" in student.keys():
        result = result + textwrap.dedent(f"""

        ### ------- PROFILE -------
        scenario name:
          personal name:
            jp: {student["profile"]["PersonalNameJp"]}

          family name:
            jp: {student["profile"]["FamilyNameJp"]} : ruby: {student["profile"]["FamilyNameRubyJp"]}

          full name:
            jp: {student["profile"]["FamilyNameJp"] + " " + student["profile"]["PersonalNameJp"]} : ruby: {student["profile"]["FamilyNameRubyJp"] + " " + student["profile"]["PersonalNameJp"]}
        
        status message:
          jp: {student["profile"]["StatusMessageJp"]}
        
        age: {student["profile"]["CharacterAgeJp"][:2] if student["profile"]["CharacterAgeJp"][:2].isdigit() else "null   # " + ("secrecy" if student["profile"]["CharacterAgeJp"][:2] == "極秘" else student["profile"]["CharacterAgeJp"][:2])}
        height: {student["profile"]["CharHeightJp"][:3]}
        school year: {student["profile"]["SchoolYearJp"][0]}

        birthday:
          day: {student["profile"]["BirthDay"].split("/")[1]}
          month: {student["profile"]["BirthDay"].split("/")[0]}
        
        hobbies:""")

        if len(re.split(", |、", student["profile"]["HobbyJp"], flags=re.UNICODE)) > 0:
            result = result + "\n"
            for hobby in re.split(", |、", student["profile"]["HobbyJp"], flags=re.UNICODE):
                result = result + "  : \"{}\"\n".format(hobby)
        else:
            result = result + ' ""\n'

        result = result + (f"""\nintroduction: [[\n{student["profile"]["ProfileIntroductionJp"]}\n]]\n""")

    return result

def toYamlString(student):
    result = textwrap.dedent(f"""\
    id: {student["Id"]}
    dev name: {student["DevName"]}
    production step: {student["ProductionStep"]} 


    ### ------- INFO -------
    name: {student["StrippedName"]}
    rarity: {student["Rarity"]}{(" - " + '★'*student["DefaultStarGrade"] + '☆'*(student["MaxStarGrade"] - student["DefaultStarGrade"])) if student["MaxStarGrade"] > 0 else ""}

    school: {student["School"]}
    club: "{student["Club"]}"
    tags: [{", ".join('"{}"'.format(tag) for tag in student["Tags"]) if len(student["Tags"]) > 0 else ''}]


    ### ------- STATUS -------
    type: {"striker" if student["SquadType"] == "Main" else "special" if student["SquadType"] == "Support" else student["SquadType"].lower()}
    role: {toEnumStr(student["TacticRole"])}
    position: {toEnumStr(student["TacticRange"])}

    armor: {toEnumStr(student["ArmorType"])}
    bullet: {toEnumStr(student["BulletType"])}

    weapon: {student["WeaponType"] if student["WeaponType"].isupper() else toEnumStr(student["WeaponType"])}
    aim ik: {toEnumStr(student["AimIKType"])}

    equipments: {"[" + ", ".join([equipment.lower() for equipment in student["EquipmentSlot"]]) + "]" if len(student["EquipmentSlot"]) > 0 else "null"}
    """)

    if student["stat"]:
        result = result + textwrap.dedent(f"""

        ### ------- STATS -------
        hp:
          min: {student["stat"]["MaxHP1"]}
          max: {student["stat"]["MaxHP100"]}
        atk:
          min: {student["stat"]["AttackPower1"]}
          max: {student["stat"]["AttackPower100"]}
        def:
          min: {student["stat"]["DefensePower1"]}
          max: {student["stat"]["DefensePower100"]}
        heal:
          min: {student["stat"]["HealPower1"]}
          max: {student["stat"]["HealPower100"]}

        stability:
          rate: {student["stat"]["StabilityRate"]} - {student["stat"]["StabilityRate"] / 100:.0f}%
          point: {student["stat"]["StabilityPoint"]}

        critical:
          crit point: {student["stat"]["CriticalPoint"]}
          crit dmg rate: {student["stat"]["CriticalDamageRate"]} - {student["stat"]["CriticalDamageRate"] / 100:.0f}%

          res point: {student["stat"]["CriticalResistPoint"]}
          res dmg rate: {student["stat"]["CriticalDamageResistRate"]} - {student["stat"]["CriticalDamageResistRate"] / 100:.0f}%
        
        oppression:
          power: {student["stat"]["OppressionPower"]}
          resist: {student["stat"]["OppressionResist"]}

        ammo:
          cost: {student["stat"]["AmmoCost"]}
          count: {student["stat"]["AmmoCount"]}

        range: {student["stat"]["Range"]}
        regen: {student["stat"]["RegenCost"]}
        dodge: {student["stat"]["DodgePoint"]}
        accuracy: {student["stat"]["AccuracyPoint"]}

        environment:
          street: {student["stat"]["StreetBattleAdaptation"]}
          indoor: {student["stat"]["IndoorBattleAdaptation"]}
          outdoor: {student["stat"]["OutdoorBattleAdaptation"]}
        """)
    
    if "profile" in student.keys():
        result = result + textwrap.dedent(f"""

        ### ------- PROFILE -------
        scenario name:
          personal name:
            jp: {student["profile"]["PersonalNameJp"]}

          family name:
            jp: {student["profile"]["FamilyNameJp"]}
            jp ruby: {student["profile"]["FamilyNameRubyJp"]}

          full name:
            jp: {student["profile"]["FamilyNameJp"] + " " + student["profile"]["PersonalNameJp"]}
            jp ruby: {student["profile"]["FamilyNameRubyJp"] + " " + student["profile"]["PersonalNameJp"]}
        
        status message:
          jp: {student["profile"]["StatusMessageJp"]}
        
        age: {student["profile"]["CharacterAgeJp"][:2] if student["profile"]["CharacterAgeJp"][:2].isdigit() else "null   # " + ("secrecy" if student["profile"]["CharacterAgeJp"][:2] == "極秘" else student["profile"]["CharacterAgeJp"][:2])}
        height: {student["profile"]["CharHeightJp"][:3]}
        school year: {student["profile"]["SchoolYearJp"][0]}

        birthday:
          day: {student["profile"]["BirthDay"].split("/")[1]}
          month: {student["profile"]["BirthDay"].split("/")[0]}
        
        hobbies:""")

        if len(re.split(",|、", student["profile"]["HobbyJp"], flags=re.UNICODE)) > 0:
            result = result + "\n"
            for hobby in re.split(",|、", student["profile"]["HobbyJp"], flags=re.UNICODE):
                result = result + "  - \"{}\"\n".format(hobby)
        else:
            result = result + ' ""\n'

        result = result + "\nintroduction: |\n  {}\n".format(student["profile"]["ProfileIntroductionJp"].replace("\n", "\n  ").replace("\n  \n", "\n\n"))

    return result

###==============================================
### Main

characterTable = {}

dataDirPath = "data/ja-JP/Excel"

filePath = os.path.join(dataDirPath, "CharacterExcelTable.json")
with open(filePath, 'r') as f:
    jsonContent = json.load(f)

    for node in jsonContent["DataList"]:
        characterTable[node["Id"]] = node
        characterTable[node["Id"]]["StrippedName"] = stripName(node["DevName"])


filePath = os.path.join(dataDirPath, "CharacterStatExcelTable.json")
with open(filePath, 'r') as f:
    jsonContent = json.load(f)

    for node in jsonContent["DataList"]:
        characterTable[node["CharacterId"]]["stat"] = node


filePath = os.path.join(dataDirPath, "LocalizeCharProfileExcelTable.json")
with open(filePath, 'r') as f:
    jsonContent = json.load(f)

    for node in jsonContent["DataList"]:
        if characterTable[node["CharacterId"]]:
            keys = [
                "StatusMessageJp",
                "FamilyNameJp",
                "FamilyNameRubyJp",
                "PersonalNameJp",
                "SchoolYearJp",
                "CharacterAgeJp",
                "BirthDay",
                "CharHeightJp",
                "HobbyJp",
                "ProfileIntroductionJp"
            ]

            hasAtleastOneKey = False
            for key in keys:
                if node[key]:
                    hasAtleastOneKey = True
                    break

            if hasAtleastOneKey:
                characterTable[node["CharacterId"]]["profile"] = {}

                for key in keys:
                    characterTable[node["CharacterId"]]["profile"][key] = node[key] or ""


###==============================================
resultDirPath = "result"
for fileType in ["zzz", "yaml"]:
    dirPath = os.path.join(resultDirPath, fileType)

    for chara in characterTable.values():
        if chara["TacticEntityType"] == "Student":
            if len(str(chara["Id"])) != 5:
                continue
            elif any(unnecessaryName in chara["DevName"].lower() for unnecessaryName in ["dummy", "tank"]):
                continue

            filePath = os.path.join(dirPath, chara["TacticEntityType"].lower(), chara["StrippedName"].lower() + "." + fileType)
            os.makedirs(os.path.dirname(filePath), exist_ok=True)

            with open(filePath, 'w') as f:
                if fileType == "yaml":
                    f.write(toYamlString(chara))
                elif fileType == "zzz":
                    f.write(toZZZString(chara))
        
        else:
            filePath = os.path.join(dirPath, chara["TacticEntityType"].lower(), chara["StrippedName"].lower() + "." + fileType)
            os.makedirs(os.path.dirname(filePath), exist_ok=True)

            with open(filePath, 'w') as f:
                if fileType == "yaml":
                    f.write(toYamlString(chara))
                elif fileType == "zzz":
                    f.write(toZZZString(chara))
