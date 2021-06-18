import std/[json, tables, strformat, strutils, os]

func getProperName(s: string): string =
    result = s
    result.removeSuffix("_default")
    result = result.replace('_', ' ')
    # wrong names by dev
    result = result.replace("Aris", "Alice")
    result = result.replace("Hihumi", "Hifumi")
    result = result.replace("Zunko", "Junko")

    result = result.capitalizeAscii()

func toEnumStr(s: string): string =
    if s.len == 0: return ""

    block:
        var tempStr = ""
        for i, c in s:
            if i == 0: tempStr.add(c); continue
            if c.isUpperAscii() and s[i-1].isAlphaAscii():
                tempStr.add('_')
            tempStr.add(c)
        
        result = tempStr
    result = result.toLowerAscii()

###==============================================
### `Student` defination
type Student* = ref object
    kind*: string

    id*: uint32
    devName*, name*: string

    rarity*: string
    star*, maxStar*: uint8

    school*: string
    club*: string
    tags*: seq[string]

    tacticRole*, tacticRange*: string
    squad*, armor*, bullet*, weapon*, aimIk*: string
    equipments*: seq[string]


### `Student` functions
func initFromJson(node: JsonNode): Student =
    result = new Student

    result.kind = node["TacticEntityType"].getStr

    result.id      = node["Id"].getInt.uint32
    result.devName = node["DevName"].getStr
    result.name    = getProperName(result.devName)

    result.rarity  = node["Rarity"].getStr
    result.star    = node["DefaultStarGrade"].getInt.uint8
    result.maxStar = node["MaxStarGrade"].getInt.uint8

    result.school = node["School"].getStr
    result.club   = node["Club"].getStr
    for tag in node["Tags"].items:
        result.tags.add tag.getStr

    result.squad  = node["SquadType"].getStr
    result.armor  = node["ArmorType"].getStr
    result.bullet = node["BulletType"].getStr
    result.weapon = node["WeaponType"].getStr
    result.aimIk  = node["AimIKType"].getStr

    result.tacticRange = node["TacticRange"].getStr
    result.tacticRole  = node["TacticRole"].getStr

    for equipment in node["EquipmentSlot"].items:
        result.equipments.add equipment.getStr

func toZzz(student: Student): string =
    result.add dedent fmt"""
    id: {student.id}
    dev name: {student.devName}


    ### ----- Info -----
    name: {student.name}
    rarity: {student.rarity}"""

    if student.star > 0:
        result.add " : "

        # add real star '★'
        for _ in 1'u8 .. student.star:
            result.add "★"
        
        # add placeholder star '☆'
        for _ in 1'u8 .. (student.maxStar - student.star):
            result.add "☆"
    
    result.add "\n\n"
    result.add dedent fmt"""
    school: {student.school}
    club: "{student.club}"
    tags:"""

    if student.tags.len == 0:
        result.add "\"\"\n"
    else:
        for i in 0 ..< student.tags.len-1:
            result.add &" \"{student.tags[i]}\" :;"
        result.add &" \"{student.tags[^1]}\""
        result.add '\n'
    result.add "\n\n"
    
    result.add dedent fmt"""
    ### ----- Status -----
    type: """
    if student.squad == "Main":
        result.add "striker\n"
    elif student.squad == "Support":
        result.add "special\n"
    else: result.add student.squad.toEnumStr & '\n'

    result.add dedent fmt"""
    role: {student.tacticRole.toEnumStr}
    position: {student.tacticRange.toEnumStr}

    armor:  {student.armor.toEnumStr}
    bullet: {student.bullet.toEnumStr}

    weapon: {student.weapon}
    aim ik: {student.aimIk.toEnumStr}

    equipments:"""
    if student.equipments.len > 0:
        for i in 0 ..< student.equipments.len-1:
            result.add &" {student.equipments[i].toEnumStr} :;"
        result.add &" {student.equipments[^1].toEnumStr}"
    result.add "\n\n\n"

    result.add dedent fmt"""
    ### ----- Stats -----
    """

func toYaml(student: Student): string =
    result.add dedent fmt"""
    id: {student.id}
    dev name: {student.devName}


    ### ----- Info -----
    name: {student.name}
    rarity: {student.rarity}"""

    if student.star > 0:
        result.add " - "

        # add real star '★'
        for _ in 1'u8 .. student.star:
            result.add "★"
        
        # add placeholder star '☆'
        for _ in 1'u8 .. (student.maxStar - student.star):
            result.add "☆"
    
    result.add "\n\n"
    result.add dedent fmt"""
    school: {student.school}
    club: "{student.club}"
    tags: ["""

    if student.tags.len == 0:
        result.add "\"\"\n"
    else:
        for i in 0 ..< student.tags.len-1:
            result.add &"\"{student.tags[i]}\", "
        result.add &"\"{student.tags[^1]}\"]"
        result.add '\n'
    result.add "\n\n"
    
    result.add dedent fmt"""
    ### ----- Status -----
    type: """
    if student.squad == "Main":
        result.add "striker\n"
    elif student.squad == "Support":
        result.add "special\n"
    else: result.add student.squad.toEnumStr & '\n'

    result.add dedent fmt"""
    role: {student.tacticRole.toEnumStr}
    position: {student.tacticRange.toEnumStr}

    armor:  {student.armor.toEnumStr}
    bullet: {student.bullet.toEnumStr}

    weapon: {student.weapon}
    aim ik: {student.aimIk.toEnumStr}

    equipments: ["""
    if student.equipments.len > 0:
        for i in 0 ..< student.equipments.len-1:
            result.add &"{student.equipments[i].toEnumStr}, "
        result.add &"{student.equipments[^1].toEnumStr}]"
    result.add "\n\n\n"

    result.add dedent fmt"""
    ### ----- Stats -----
    """

###=============================================
# directory contains all json files
let dirPath = "data/ja-JP/Excel"

# result table
var stundentTable = newTable[uint32, Student]()


# load 'CharacterExcelTable.json'
block:
    let
      fileName = "CharacterExcelTable.json"
      filePath = dirPath / fileName
    
    let jsonContent = parseFile(filePath)["DataList"]
    for node in jsonContent.items:
        block blk:
            # early out if node type is not student
            if node["TacticEntityType"].getStr != "Student": continue
            if node["Id"].getInt.intToStr.len != 5: continue

            for unnecessaryName in ["dummy", "tank"]:
                if node["DevName"].getStr.toLowerAscii().contains(unnecessaryName):
                    break blk

            let student = initFromJson(node)
            stundentTable[student.id] = student

when isMainModule:
    let destDir = "result"

    for node in stundentTable.values:
        block:
            let destDir  = destDir / "zzz"
            createDir(destDir)

            let
              fileName = node.name.toLowerAscii() & ".zzz"
              filePath = destDir / fileName
            writeFile(filePath, node.toZzz())

        block:
            let destDir  = destDir / "yaml"
            createDir(destDir)

            let
              fileName = node.name.toLowerAscii() & ".yaml"
              filePath = destDir / fileName
            writeFile(filePath, node.toYaml())