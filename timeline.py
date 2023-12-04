import csv
import datetime
import math
import sys
from PIL import Image, ImageDraw, ImageFont


NOW = datetime.date.today().year
COUNT_P = 0
MARRIAGE = {"starts": 0, "ends": 0}
STEP = 1
START_DATE = 0
W_LINE_STARTS = START_DATE
H_LINE_STARTS = START_DATE
W_ID = 0
H_ID = 0
W_F_NAME = ""
H_F_NAME = ""
W_S_NAME = ""
H_S_NAME = ""
H_BORN = 0
W_BORN = 0
H_DIED = 0
W_DIED = 0
W_CH_NUM = 0
H_CH_NUM = 0
C_CH_NUM = 0

img = Image.new("RGBA", (2500, 1200), (240, 230, 168))
draw = ImageDraw.Draw(img)
font_reg = ImageFont.truetype(r"Amelies.ttf", 20)
font = ImageFont.truetype(r"Amelies.ttf", 30)
font_title = ImageFont.truetype(r"Amelies.ttf", 35)


class Person:
    def __init__(
        self,
        id,
        f_name=None,
        s_name=None,
        born=None,
        died=None,
        children=None,
        events=None,
    ):
        self.id = id
        self.f_name = f_name
        self.s_name = s_name
        self.born = born
        self.died = died
        self.children = children
        self.events = events

    @classmethod
    def get(cls, id1):
        try:
            with open("persons.csv", encoding="utf-8") as persons:
                reader = csv.DictReader(persons)
                for row in reader:
                    if id1 == row["id"]:
                        id = row["id"]
                        f_name = row["vardas"]
                        s_name = row["pavarde"]
                        global COUNT_P
                        COUNT_P = 1
        except FileNotFoundError:
            print("file not found")
            sys.exit()

        born = None
        died = None
        children = []
        events = []
        try:
            with open("facts.csv", encoding="utf-8") as facts:
                reader2 = csv.DictReader(facts)
                for row in reader2:
                    if id1 == row["ivykio_asm_id"] and row["ivykio_tipas"] == "01":
                        born = row["pradzia"]
                    elif (
                        id1 == row["asm_id"]
                        and id1 == row["ivykio_asm_id"]
                        and row["ivykio_tipas"] == "02"
                    ):
                        died = row["pradzia"]
                    elif (
                        id1 == row["asm_id"]
                        and row["ivykio_tipas"] == "01"
                        and row["ivykio_asm_id"] != row["asm_id"]
                    ):
                        children.append(row["ivykio_asm_id"])
                    elif id1 == row["asm_id"] and (
                        row["ivykio_tipas"] == "03" or row["ivykio_tipas"] == "04"
                    ):
                        events.append(
                            {
                                "event_id": row["ivykio_id"],
                                "event_type": row["ivykio_tipas"],
                                "starts": row["pradzia"],
                                "ends": row["pabaiga"],
                                "event_extent": row["ivykio_mastas"],
                                "event_pers_id": row["ivykio_asm_id"],
                                "descr": row["ivykis"],
                            }
                        )

        except FileNotFoundError:
            print("file not found")
            sys.exit()

        if COUNT_P > 0:
            return cls(id, f_name, s_name, born, died, children, events)
        else:
            raise ValueError


def main():
    try:
        husband = Person.get(input("Husband ID: ").strip())
    except Exception:
        print("Person not found")
        husband = None

    try:
        wife = Person.get(input("Wife ID: ").strip())
    except Exception:
        print("Person not found")
        sys.exit()

    global W_ID
    W_ID = wife.id

    if husband is not None:
        global H_ID
        H_ID = husband.id

    global W_F_NAME
    if wife.f_name.strip() != "":
        W_F_NAME = wife.f_name
    else:
        W_F_NAME = "............"

    global W_S_NAME
    if wife.s_name.strip() != "":
        W_S_NAME = wife.s_name
    else:
        W_S_NAME = "............"

    if husband is not None:
        global H_F_NAME
        if husband.f_name.strip() != "":
            H_F_NAME = husband.f_name
        else:
            H_F_NAME = "............"

        global H_S_NAME
        if husband.s_name.strip() != "":
            H_S_NAME = husband.s_name
        else:
            H_S_NAME = "............"

    try:
        global MARRIAGE
        MARRIAGE = get_marriage(husband, wife)
    except ValueError:
        print("These persons haven't been married")
        sys.exit()

    if MARRIAGE is None:
        print("These persons haven't been married")
        sys.exit()

    if int(MARRIAGE["starts"]) == 0 and int(MARRIAGE["ends"]) == 0:
        print("Enter the date of marriage of these persons")
        sys.exit()

    if husband is not None:
        if husband.born is not None:
            try:
                global H_BORN
                H_BORN = int(husband.born)
            except Exception:
                H_BORN = None

        else:
            H_BORN = None
    else:
        H_BORN = None

    if wife.born is not None:
        try:
            global W_BORN
            W_BORN = int(wife.born)
        except Exception:
                W_BORN = None
    else:
        W_BORN = None

    if husband is not None:
        if husband.died is not None:
            try:
                global H_DIED
                H_DIED = int(husband.died)
            except Exception:
                H_DIED = None
        else:
            H_DIED = None
    else:
        H_DIED = None

    if wife.died is not None:
        try:
            global W_DIED
            W_DIED = int(wife.died)
        except Exception:
                W_DIED = None
    else:
        W_DIED = None

    global START_DATE
    if husband is not None:
        START_DATE = get_start_date_b(MARRIAGE, H_BORN, W_BORN)
    else:
        START_DATE = get_start_date_w(W_BORN, W_DIED)
    draw_grid()

    draw_parents_lines(husband, wife)

    if husband is not None:
        h_children = husband.children
    else:
        h_children = None

    w_children = wife.children

    ord_child_list = ordered_child_list(h_children, w_children)

    draw_ch_lifelines(ord_child_list)

    if husband is not None:
        draw_fam_event_dots(wife.events, husband.events)
    else:
        draw_event_dots(wife.events)

    if husband is not None:
        print(f"{H_F_NAME} {H_S_NAME}")
        print(f"{W_F_NAME} {W_S_NAME}")
    else:
        print(f"{W_F_NAME} {W_S_NAME}")


# function returns marriage dates
def get_marriage(hu, wi):
    marriage = {"starts": 0, "ends": 0}
    wi_marriage = {"starts": 0, "ends": 0}
    hu_marriage = {"starts": 0, "ends": 0}
    if hu is not None:
        for event in hu.events:
            if event["event_type"] == "03" and event["event_pers_id"] == wi.id:
                if event["starts"].strip() != "" and event["ends"].strip() != "":
                    hu_marriage = {"starts": event["starts"], "ends": event["ends"]}
                elif event["starts"].strip() != "" and event["ends"].strip() == "":
                    hu_marriage = {"starts": event["starts"], "ends": 0}
                elif event["starts"].strip() == "" and event["ends"].strip() != "":
                    hu_marriage = {"starts": 0, "ends": event["ends"]}
                else:
                    hu_marriage = {"starts": 0, "ends": 0}

        for event in wi.events:
            if event["event_type"] == "03" and event["event_pers_id"] == hu.id:
                if event["starts"].strip() != "" and event["ends"].strip() != "":
                    wi_marriage = {"starts": event["starts"], "ends": event["ends"]}
                elif event["starts"].strip() != "" and event["ends"].strip() == "":
                    wi_marriage = {"starts": event["starts"], "ends": 0}
                elif event["starts"].strip() == "" and event["ends"].strip() != "":
                    wi_marriage = {"starts": 0, "ends": event["ends"]}
                else:
                    wi_marriage = {"starts": 0, "ends": 0}

        if int(hu_marriage["starts"]) == 0 and int(wi_marriage["starts"]) == 0:
            marriage["starts"] = 0
        elif int(wi_marriage["starts"]) > int(hu_marriage["starts"]):
            marriage["starts"] = wi_marriage["starts"]
        else:
            marriage["starts"] = hu_marriage["starts"]

        if int(hu_marriage["ends"]) == 0 and int(wi_marriage["ends"]) == 0:
            marriage["ends"] = 0
        elif int(wi_marriage["ends"]) > int(hu_marriage["ends"]):
            marriage["ends"] = wi_marriage["ends"]
        else:
            marriage["ends"] = hu_marriage["ends"]

        return marriage
    else:
        return None


# function calculate grid start date when both spouses are known
def get_start_date_b(mar, h_born, w_born):
    if h_born is not None and w_born is not None:
        if h_born > w_born:
            start_date = math.floor(w_born / 10) * 10
        else:
            start_date = math.floor(h_born / 10) * 10
    elif h_born is None and w_born is not None:
        start_date = math.floor(w_born / 10) * 10
    elif h_born is not None and w_born is None:
        start_date = math.floor(int(h_born) / 10) * 10
    else:
        start_date = math.floor((mar - 50) / 10) * 10
    return start_date


# function calculate grid start date when only wife is known
def get_start_date_w(w_born, w_died):
    if w_born is not None:
        start_date = math.floor(w_born / 10) * 10
    else:
        if w_died is not None:
            start_date = math.floor((w_died - 100) / 10) * 10
        else:
            sys.exit("The dataset does not contain the woman date of birth or death")
    return start_date


# function draws a grid with dates
def draw_grid():
    # calculate how many picsels correspond 1 year
    global STEP
    STEP = 2400 / 150
    step2 = 2400 / 150 - 5

    # draw a bright line every 10 years and a fainter one every 5 years
    for i in range(16):
        draw.line(
            ((STEP * 2 + (i * STEP * 10)), 100, (STEP * 2 + (i * STEP * 10)), 1200),
            fill=(163, 146, 39),
            width=1,
        )
        draw.line(
            ((STEP * 7 + (i * STEP * 10)), 100, (STEP * 7 + (i * STEP * 10)), 1200),
            fill=(219, 195, 44),
            width=1,
        )
        draw.text(
            (((step2 * 2) + (i * STEP * 10)), 50),
            str(START_DATE + i * 10),
            font=font,
            fill=(163, 146, 39),
        )
    img.save("family_timeline.png")


# function draws parent life lines
def draw_parents_lines(hus, wif):
    if MARRIAGE is not None:
        marriage_point = STEP * 2 + STEP * (int(MARRIAGE["starts"]) - START_DATE)

        if W_BORN is not None:
            global W_LINE_STARTS
            W_LINE_STARTS = STEP * 2 + STEP * (int(W_BORN) - START_DATE)
            draw.text(
                (W_LINE_STARTS + 5, 646),
                f"{W_BORN}  was born {W_F_NAME} {W_S_NAME}",
                font=font_reg,
                fill=(107, 24, 93),
            )
        else:
            W_LINE_STARTS = STEP * 2 + STEP * (int(MARRIAGE["starts"]) - START_DATE)
            draw.text(
                (marriage_point - 350, 646),
                f"????  was born {W_F_NAME} {W_S_NAME}",
                font=font_reg,
                fill=(107, 24, 93),
            )

        if hus is not None:
            if H_BORN is not None:
                global H_LINE_STARTS
                H_LINE_STARTS = STEP * 2 + STEP * (int(hus.born) - START_DATE)
                draw.text(
                    (H_LINE_STARTS + 5, 683),
                    f"{hus.born}  was born {H_F_NAME} {H_S_NAME}",
                    font=font_reg,
                    fill=(107, 24, 93),
                )
            else:
                H_LINE_STARTS = STEP * 2 + STEP * (int(MARRIAGE["starts"]) - START_DATE)
                draw.text(
                    (marriage_point - 300, 683),
                    f"????  was born {H_F_NAME} {H_S_NAME}",
                    font=font_reg,
                    fill=(107, 24, 93),
                )

        if wif.died is not None:
            end_w = STEP * 2 + STEP * (int(wif.died) - START_DATE)
            draw.line(
                (W_LINE_STARTS, 675, marriage_point, 675),
                fill=(168, 29, 91, 99),
                width=5,
            )
            draw.line((marriage_point, 675, end_w, 675), fill=(168, 29, 91), width=5)
        else:
            draw.line(
                (W_LINE_STARTS, 675, marriage_point, 675),
                fill=(168, 29, 91, 99),
                width=5,
            )
            draw.line(
                (marriage_point, 675, STEP * 2 + STEP * (NOW - START_DATE), 675),
                fill=(168, 29, 91),
                width=5,
            )
            draw.line(
                (STEP * 2 + STEP * (NOW - START_DATE), 675, 2900, 675),
                fill=(168, 29, 91, 99),
                width=5,
            )

        if hus is not None:
            if hus.died is not None:
                end_h = STEP * 2 + STEP * (int(hus.died) - START_DATE)
                draw.line(
                    (H_LINE_STARTS, 681, marriage_point, 681),
                    fill=(97, 27, 140, 99),
                    width=5,
                )
                draw.line(
                    (marriage_point, 681, end_h, 681), fill=(97, 27, 140), width=5
                )
                draw.ellipse((end_h - 9, 671, end_h + 9, 689), fill=(107, 24, 93))
                draw.text(
                    (end_h + 13, 678),
                    f"{hus.died}  died {H_F_NAME} {H_S_NAME}",
                    font=font_reg,
                    fill=(107, 24, 93),
                )
            else:
                draw.line(
                    (H_LINE_STARTS, 681, marriage_point, 681),
                    fill=(97, 27, 140, 99),
                    width=5,
                )
                draw.line(
                    (marriage_point, 681, STEP * 2 + STEP * (NOW - START_DATE), 681),
                    fill=(97, 27, 140),
                    width=5,
                )
                draw.line(
                    (STEP * 2 + STEP * (NOW - START_DATE), 681, 2900, 681),
                    fill=(97, 27, 140, 99),
                    width=5,
                )

        draw.line(
            (marriage_point - 45, 135, marriage_point + 1000, 135),
            fill=(168, 29, 91, 80),
            width=8,
        )
        draw.line(
            (marriage_point, 672, marriage_point, 135), fill=(168, 29, 91, 80), width=4
        )

        draw.ellipse(
            (W_LINE_STARTS - 10, 665, W_LINE_STARTS + 10, 685),
            fill=(168, 29, 91, 99),
            outline=(240, 230, 168),
        )
        draw.ellipse(
            (W_LINE_STARTS - 3, 671, W_LINE_STARTS + 3, 679),
            fill=(240, 230, 168),
            outline=(240, 230, 168),
        )
        draw.ellipse(
            (H_LINE_STARTS - 10, 670, H_LINE_STARTS + 10, 690),
            fill=(97, 27, 140, 99),
            outline=(240, 230, 168),
        )
        draw.ellipse(
            (H_LINE_STARTS - 3, 676, H_LINE_STARTS + 3, 684),
            fill=(240, 230, 168),
            outline=(240, 230, 168),
        )
        draw.ellipse(
            (marriage_point - 13, 665, marriage_point + 13, 691),
            fill=(107, 24, 93),
            outline=(240, 230, 168),
        )
        draw.ellipse(
            (marriage_point - 6, 672, marriage_point + 6, 684),
            fill=(240, 230, 168),
            outline=(240, 230, 168),
        )
        draw.ellipse(
            (marriage_point - 4, 674, marriage_point + 4, 682),
            fill=(107, 24, 93),
            outline=(240, 230, 168),
        )

        if MARRIAGE["ends"] != "":
            draw.line(
                (
                    (STEP * 2 + STEP * (int(MARRIAGE["ends"]) - START_DATE)),
                    829,
                    (STEP * 2 + STEP * (int(MARRIAGE["ends"]) - START_DATE) + 500),
                    829,
                ),
                fill=(168, 29, 91, 80),
                width=4,
            )
            draw.line(
                (
                    (STEP * 2 + STEP * (int(MARRIAGE["ends"]) - START_DATE)),
                    672,
                    (STEP * 2 + STEP * (int(MARRIAGE["ends"]) - START_DATE)),
                    829,
                ),
                fill=(168, 29, 91, 80),
                width=4,
            )
            draw.ellipse(
                (
                    STEP * 2 + STEP * (int(MARRIAGE["ends"]) - START_DATE) - 10,
                    668,
                    STEP * 2 + STEP * (int(MARRIAGE["ends"]) - START_DATE) + 10,
                    688,
                ),
                fill=(107, 24, 93),
            )
            draw.ellipse(
                (
                    STEP * 2 + STEP * (int(MARRIAGE["ends"]) - START_DATE) - 2,
                    676,
                    STEP * 2 + STEP * (int(MARRIAGE["ends"]) - START_DATE) + 2,
                    680,
                ),
                fill=(240, 230, 168),
            )

            if hus is not None and wif is not None:
                draw.text((STEP * 2 + STEP * (int(MARRIAGE["ends"]) - START_DATE) + 12, 805),
                          f"{int(MARRIAGE['ends'])} {W_F_NAME} {W_S_NAME} and {H_F_NAME} {H_S_NAME} have broken up",
                          font=font_reg, fill=(107, 24, 93))
            elif hus is None and wif is not None:
                draw.text((STEP * 2 + STEP * (int(MARRIAGE["ends"]) - START_DATE) + 12, 805),
                          f"{int(MARRIAGE['ends'])} {W_F_NAME} {W_S_NAME} and unknown person have broken up",
                          font=font_reg, fill=(107, 24, 93))

        if hus is not None and wif is not None:
            draw.text((STEP * 2 + STEP * (int(MARRIAGE["starts"]) - START_DATE) - 40, 95),
                      f"{int(MARRIAGE['starts'])} got married {W_F_NAME} {W_S_NAME} and {H_F_NAME} {H_S_NAME}",
                      font=font_title, fill=(107, 24, 93))
        elif hus is None and wif is not None:
            draw.text((STEP * 2 + STEP * (int(MARRIAGE["starts"]) - START_DATE) - 40, 95),
                      f"{int(MARRIAGE['starts'])} got married {W_F_NAME} {wif.s_name} and unknown person",
                      font=font_title, fill=(107, 24, 93))
        elif hus is not None and wif is None:
            draw.text((STEP * 2 + STEP * (int(MARRIAGE["starts"]) - START_DATE) - 40, 95),
                      f"{int(MARRIAGE['starts'])} got married {H_F_NAME} {H_S_NAME} and unknown person",
                      font=font_title, fill=(107, 24, 93))

        if wif.died is not None:
            draw.ellipse((end_w - 9, 666, end_w + 9, 684), fill=(107, 24, 93))
            draw.text(
                (end_w + 13, 656),
                f"{wif.died}  died {W_F_NAME} {W_S_NAME}",
                font=font_reg,
                fill=(107, 24, 93),
            )

    else:
        if W_BORN is not None:
            W_LINE_STARTS = STEP * 2 + STEP * (int(W_BORN) - START_DATE)
            draw.text(
                (W_LINE_STARTS + 5, 646),
                f"{W_BORN}  was born {W_F_NAME} {W_S_NAME}",
                font=font_reg,
                fill=(107, 24, 93),
            )
        else:
            W_LINE_STARTS = STEP * 2
            draw.text(
                (W_LINE_STARTS + 5, 646),
                f"????  was born {W_F_NAME} {W_S_NAME}",
                font=font_reg,
                fill=(107, 24, 93),
            )

        if wif.died is not None:
            end_w = W_LINE_STARTS + STEP * (int(wif.died) - int(wif.born))
            draw.line((W_LINE_STARTS, 675, end_w, 675), fill=(168, 29, 91), width=5)
            draw.ellipse((end_w - 9, 666, end_w + 9, 684), fill=(107, 24, 93))
            draw.text(
                (end_w + 13, 656),
                f"{wif.died}  died {W_F_NAME} {W_S_NAME}",
                font=font_reg,
                fill=(107, 24, 93),
            )
        else:
            draw.line(
                (W_LINE_STARTS, 675, STEP * 2 + STEP * (NOW - START_DATE), 675),
                fill=(168, 29, 91),
                width=5,
            )
            draw.line(
                (STEP * 2 + STEP * (NOW - START_DATE), 675, 2900, 675),
                fill=(168, 29, 91, 99),
                width=5,
            )

        draw.ellipse(
            (W_LINE_STARTS - 10, 665, W_LINE_STARTS + 10, 685),
            fill=(168, 29, 91, 99),
            outline=(240, 230, 168),
        )
        draw.ellipse(
            (W_LINE_STARTS - 3, 671, W_LINE_STARTS + 3, 679),
            fill=(240, 230, 168),
            outline=(240, 230, 168),
        )

        if hus is not None:
            if H_BORN is not None:
                H_LINE_STARTS = STEP * 2 + STEP * (int(hus.born) - START_DATE)
                draw.text(
                    (H_LINE_STARTS + 5, 683),
                    f"{hus.born}  was born {H_F_NAME} {H_S_NAME}",
                    font=font_reg,
                    fill=(107, 24, 93),
                )
            else:
                H_LINE_STARTS = STEP * 2
                draw.text(
                    (H_LINE_STARTS + 5, 683),
                    f"????  was born {H_F_NAME} {H_S_NAME}",
                    font=font_reg,
                    fill=(107, 24, 93),
                )

            if hus.died is not None:
                end_h = H_LINE_STARTS + STEP * (int(hus.died) - int(hus.born))
                draw.line((H_LINE_STARTS, 681, end_h, 681), fill=(97, 27, 140), width=5)
                draw.ellipse((end_h - 9, 671, end_h + 9, 689), fill=(107, 24, 93))
                draw.text(
                    (end_h + 13, 678),
                    f"{hus.died}  died {H_F_NAME} {H_S_NAME}",
                    font=font_reg,
                    fill=(107, 24, 93),
                )
                draw.ellipse(
                    (H_LINE_STARTS - 10, 670, H_LINE_STARTS + 10, 690),
                    fill=(97, 27, 140, 99),
                    outline=(240, 230, 168),
                )
                draw.ellipse(
                    (H_LINE_STARTS - 3, 676, H_LINE_STARTS + 3, 684),
                    fill=(240, 230, 168),
                    outline=(240, 230, 168),
                )
            else:
                draw.line((H_LINE_STARTS, 681, NOW, 681), fill=(97, 27, 140), width=5)
                draw.line((NOW, 681, 2900, 681), fill=(97, 27, 140, 99), width=5)

        draw.line((145, 135, 900, 135), fill=(168, 29, 91, 80), width=8)
        if hus is not None:
            draw.text(
                (150, 95),
                f"{W_F_NAME} {W_S_NAME} and {H_F_NAME} {H_S_NAME}",
                font=font_title,
                fill=(107, 24, 93),
            )
        else:
            draw.text(
                (150, 95), f"{W_F_NAME} {W_S_NAME}", font=font_title, fill=(107, 24, 93)
            )

    img.save("family_timeline.png")


def get_other_ev_wp(w_ev):
    other_ev_wp = []

    for event in w_ev:
        if MARRIAGE is not None:
            if MARRIAGE["starts"] != 0 and MARRIAGE["ends"] != 0:
                if (
                    (
                        event["event_type"] == "04"
                        and event["event_extent"] == "01"
                        and event["event_pers_id"] == W_ID
                    )
                    or (
                        event["event_type"] == "04"
                        and event["event_extent"] == "02"
                        and (
                            int(event["starts"]) < int(MARRIAGE["starts"])
                            or (int(event["starts"]) > int(MARRIAGE["ends"]))
                        )
                    )
                    or (event["event_type"] == "03" and event["event_pers_id"] != H_ID)
                ):
                    other_ev_wp.append(event)
            elif MARRIAGE["starts"] != 0 and MARRIAGE["ends"] == 0:
                if (
                    (
                        event["event_type"] == "04"
                        and event["event_extent"] == "01"
                        and event["event_pers_id"] == W_ID
                    )
                    or (
                        event["event_type"] == "04"
                        and event["event_extent"] == "02"
                        and (int(event["starts"]) < int(MARRIAGE["starts"]))
                    )
                    or (event["event_type"] == "03" and event["event_pers_id"] != H_ID)
                ):
                    other_ev_wp.append(event)
        else:
            if (
                event["event_type"] == "04"
                and event["event_extent"] == "01"
                and event["event_pers_id"] == W_ID
            ) or (event["event_type"] == "03" and event["event_pers_id"] != H_ID):
                other_ev_wp.append(event)

    return other_ev_wp


def get_other_ev_hp(h_ev):
    other_ev_hp = []

    for event in h_ev:
        if MARRIAGE is not None:
            if MARRIAGE["starts"] != 0 and MARRIAGE["ends"] != 0:
                if (
                    (
                        event["event_type"] == "04"
                        and event["event_extent"] == "01"
                        and event["event_pers_id"] == H_ID
                    )
                    or (
                        event["event_type"] == "04"
                        and event["event_extent"] == "02"
                        and (
                            int(event["starts"]) < int(MARRIAGE["starts"])
                            or (int(event["starts"]) > int(MARRIAGE["ends"]))
                        )
                    )
                    or (event["event_type"] == "03" and event["event_pers_id"] != W_ID)
                ):
                    other_ev_hp.append(event)
            elif MARRIAGE["starts"] != 0 and MARRIAGE["ends"] == 0:
                if (
                    (
                        event["event_type"] == "04"
                        and event["event_extent"] == "01"
                        and event["event_pers_id"] == H_ID
                    )
                    or (
                        event["event_type"] == "04"
                        and event["event_extent"] == "02"
                        and (int(event["starts"]) < int(MARRIAGE["starts"]))
                    )
                    or (event["event_type"] == "03" and event["event_pers_id"] != W_ID)
                ):
                    other_ev_hp.append(event)
        else:
            if (
                event["event_type"] == "04"
                and event["event_extent"] == "01"
                and event["event_pers_id"] == H_ID
            ) or (event["event_type"] == "03" and event["event_pers_id"] != W_ID):
                other_ev_hp.append(event)

    return other_ev_hp


def get_other_ev_fp(w_ev, h_ev):
    other_ev_fp = []

    if MARRIAGE is not None:
        if MARRIAGE["starts"] != 0 and MARRIAGE["ends"] != 0:
            for event in w_ev:
                if (
                    event["event_type"] == "04"
                    and event["event_extent"] == "02"
                    and (
                        int(event["starts"]) > int(MARRIAGE["starts"])
                        and int(event["starts"]) < int(MARRIAGE["ends"])
                    )
                ) or (
                    event["event_type"] == "04"
                    and event["event_extent"] == "01"
                    and event["event_pers_id"] != W_ID
                    and (
                        int(event["starts"]) > int(MARRIAGE["starts"])
                        and int(event["starts"]) < int(MARRIAGE["ends"])
                    )
                ):
                    other_ev_fp.append(event)
            for event in h_ev:
                if (
                    event["event_type"] == "04"
                    and event["event_extent"] == "02"
                    and (
                        int(event["starts"]) > int(MARRIAGE["starts"])
                        and int(event["starts"]) < int(MARRIAGE["ends"])
                    )
                ) or (
                    event["event_type"] == "04"
                    and event["event_extent"] == "01"
                    and event["event_pers_id"] != H_ID
                    and (
                        int(event["starts"]) > int(MARRIAGE["starts"])
                        and int(event["starts"]) < int(MARRIAGE["ends"])
                    )
                ):
                    other_ev_fp.append(event)
        elif MARRIAGE["starts"] != 0 and MARRIAGE["ends"] == 0:
            for event in w_ev:
                if (
                    event["event_type"] == "04"
                    and event["event_extent"] == "02"
                    and (int(event["starts"]) > int(MARRIAGE["starts"]))
                ) or (
                    event["event_type"] == "04"
                    and event["event_extent"] == "01"
                    and event["event_pers_id"] != W_ID
                    and (int(event["starts"]) > int(MARRIAGE["starts"]))
                ):
                    other_ev_fp.append(event)
            for event in h_ev:
                if (
                    event["event_type"] == "04"
                    and event["event_extent"] == "02"
                    and (int(event["starts"]) > int(MARRIAGE["starts"]))
                ) or (
                    event["event_type"] == "04"
                    and event["event_extent"] == "01"
                    and event["event_pers_id"] != H_ID
                    and (int(event["starts"]) > int(MARRIAGE["starts"]))
                ):
                    other_ev_fp.append(event)
    return other_ev_fp


# function draws dots to indicate family life events and semicircles to indicate wife or husband life events
def draw_fam_event_dots(w_ev, h_ev):
    other_ev_wp = get_other_ev_wp(w_ev)
    other_ev_hp = get_other_ev_hp(h_ev)
    other_ev_fp = get_other_ev_fp(w_ev, h_ev)

    # write events titles
    other_ev_wt = other_ev_wp
    other_ev_ht = other_ev_hp
    last_point = 1
    total_other_ev = other_ev_wp + other_ev_hp + other_ev_fp

    try:
        max_h = round(len(total_other_ev) / 2) - len(other_ev_hp)
    except Exception:
        max_h = 0
    try:
        max_w = math.floor(len(total_other_ev) / 2) - len(other_ev_wp)
    except Exception:
        max_w = 0

    for event in other_ev_fp:
        if max_h > 0:
            period_from = int(event["starts"]) - 10
            period_till = int(event["starts"]) + 10
            count_w_ev = 0
            for ev in other_ev_wp:
                if int(ev["starts"]) > period_from and int(ev["starts"]) < period_till:
                    count_w_ev += 1
            count_h_ev = 0
            for ev in other_ev_hp:
                if int(ev["starts"]) > period_from and int(ev["starts"]) < period_till:
                    count_h_ev += 1
            if count_h_ev > count_w_ev:
                other_ev_wt.append(event)
                max_w -= 1
            elif count_w_ev > count_h_ev:
                other_ev_ht.append(event)
                max_h -= 1
            else:
                if last_point == 0 and max_w > 0:
                    other_ev_wt.append(event)
                    max_w -= 1
                    last_point = 1
                else:
                    other_ev_ht.append(event)
                    max_h -= 1
                    last_point = 0
        else:
            other_ev_wt.append(event)
            max_w -= 1

    other_ev_wt = sorted(
        other_ev_wt, reverse=True, key=lambda other_ev_wt: other_ev_wt["starts"]
    )
    other_ev_ht = sorted(
        other_ev_ht, reverse=True, key=lambda other_ev_ht: other_ev_ht["starts"]
    )

    j = 0
    while j < len(other_ev_wt):
        i = 0
        while (i < 7) and (j < len(other_ev_wt)):
            draw.line(
                (
                    (STEP * 2 + STEP * (int(other_ev_wt[j]["starts"]) - START_DATE)),
                    640 - (i * 18),
                    (
                        STEP * 2
                        + STEP * (int(other_ev_wt[j]["starts"]) - START_DATE)
                        + 6
                    ),
                    640 - (i * 18),
                ),
                fill=(107, 24, 93, 99),
                width=2,
            )
            draw.line(
                (
                    (STEP * 2 + STEP * (int(other_ev_wt[j]["starts"]) - START_DATE)),
                    640 - (i * 18),
                    (STEP * 2 + STEP * (int(other_ev_wt[j]["starts"]) - START_DATE)),
                    672,
                ),
                fill=(107, 24, 93, 80),
                width=2,
            )
            if other_ev_wt[j]["event_type"] == "03":
                draw.text(
                    (
                        (
                            STEP * 2
                            + STEP * (int(other_ev_wt[j]["starts"]) - START_DATE)
                            + 7
                        ),
                        629 - (i * 18),
                    ),
                    f"{other_ev_wt[j]['starts']}  {W_F_NAME} {W_S_NAME} {other_ev_wt[j]['descr']}",
                    font=font_reg,
                    fill=(107, 24, 93),
                )
            else:
                try:
                    ev_pers = Person.get(other_ev_wt[j]["event_pers_id"])
                    draw.text(
                        (
                            (
                                STEP * 2
                                + STEP * (int(other_ev_wt[j]["starts"]) - START_DATE)
                                + 7
                            ),
                            629 - (i * 18),
                        ),
                        f"{other_ev_wt[j]['starts']}  {ev_pers.f_name} {other_ev_wt[j]['descr']}",
                        font=font_reg,
                        fill=(107, 24, 93),
                    )
                except UnboundLocalError:
                    draw.text(
                        (
                            (
                                STEP * 2
                                + STEP * (int(other_ev_wt[j]["starts"]) - START_DATE)
                                + 7
                            ),
                            629 - (i * 18),
                        ),
                        f"{other_ev_wt[j]['starts']}  {other_ev_wt[j]['descr']}",
                        font=font_reg,
                        fill=(107, 24, 93),
                    )
            j += 1
            i += 1

    img.save("family_timeline.png")

    k = 0
    while k < len(other_ev_ht):
        l = 0
        while (l < 7) and (k < len(other_ev_ht)):
            draw.line(
                (
                    (STEP * 2 + STEP * (int(other_ev_ht[k]["starts"]) - START_DATE)),
                    703 + (l * 18),
                    (
                        STEP * 2
                        + STEP * (int(other_ev_ht[k]["starts"]) - START_DATE)
                        + 6
                    ),
                    703 + (l * 18),
                ),
                fill=(107, 24, 93, 99),
                width=2,
            )
            draw.line(
                (
                    (STEP * 2 + STEP * (int(other_ev_ht[k]["starts"]) - START_DATE)),
                    703 + (l * 18),
                    (STEP * 2 + STEP * (int(other_ev_ht[k]["starts"]) - START_DATE)),
                    672,
                ),
                fill=(107, 24, 93, 80),
                width=2,
            )
            if other_ev_ht[k]["event_type"] == "03":
                draw.text(
                    (
                        (
                            STEP * 2
                            + STEP * (int(other_ev_ht[k]["starts"]) - START_DATE)
                            + 7
                        ),
                        698 + (l * 18),
                    ),
                    f"{other_ev_ht[k]['starts']}  {H_F_NAME} {H_S_NAME} {other_ev_ht[k]['descr']}",
                    font=font_reg,
                    fill=(107, 24, 93),
                )
            else:
                try:
                    ev_pers = Person.get(other_ev_ht[k]["event_pers_id"])
                    draw.text(
                        (
                            (
                                STEP * 2
                                + STEP * (int(other_ev_ht[k]["starts"]) - START_DATE)
                                + 7
                            ),
                            698 + (l * 18),
                        ),
                        f"{other_ev_ht[k]['starts']}  {ev_pers.f_name} {other_ev_ht[k]['descr']}",
                        font=font_reg,
                        fill=(107, 24, 93),
                    )
                except UnboundLocalError:
                    draw.text(
                        (
                            (
                                STEP * 2
                                + STEP * (int(other_ev_ht[k]["starts"]) - START_DATE)
                                + 7
                            ),
                            698 + (l * 18),
                        ),
                        f"{other_ev_ht[k]['starts']}  {other_ev_ht[k]['descr']}",
                        font=font_reg,
                        fill=(107, 24, 93),
                    )
            k += 1
            l += 1

    img.save("family_timeline.png")

    # function draws semicircles to indicate wife life events
    for event in other_ev_wp:
        if MARRIAGE is not None:
            if int(event["starts"]) < int(MARRIAGE["starts"]) or (
                int(MARRIAGE["ends"]) != 0
                and int(event["starts"]) > int(MARRIAGE["ends"])
            ):
                draw.arc(
                    [
                        (
                            (
                                STEP * 2
                                + STEP * (int(event["starts"]) - START_DATE)
                                - 10
                            ),
                            669,
                        ),
                        (
                            (
                                STEP * 2
                                + STEP * (int(event["starts"]) - START_DATE)
                                + 10
                            ),
                            687,
                        ),
                    ],
                    start=180,
                    end=0,
                    fill=(168, 29, 91, 99),
                    width=6,
                )
                draw.ellipse(
                    (
                        STEP * 2 + STEP * (int(event["starts"]) - START_DATE) - 4,
                        673,
                        STEP * 2 + STEP * (int(event["starts"]) - START_DATE) + 4,
                        683,
                    ),
                    fill=(240, 230, 168),
                )
            else:
                draw.arc(
                    [
                        (
                            (
                                STEP * 2
                                + STEP * (int(event["starts"]) - START_DATE)
                                - 10
                            ),
                            669,
                        ),
                        (
                            (
                                STEP * 2
                                + STEP * (int(event["starts"]) - START_DATE)
                                + 10
                            ),
                            687,
                        ),
                    ],
                    start=180,
                    end=0,
                    fill=(168, 29, 91),
                    width=6,
                )
                draw.ellipse(
                    (
                        STEP * 2 + STEP * (int(event["starts"]) - START_DATE) - 4,
                        673,
                        STEP * 2 + STEP * (int(event["starts"]) - START_DATE) + 4,
                        683,
                    ),
                    fill=(240, 230, 168),
                )
        else:
            draw.arc(
                [
                    ((STEP * 2 + STEP * (int(event["starts"]) - START_DATE) - 10), 669),
                    ((STEP * 2 + STEP * (int(event["starts"]) - START_DATE) + 10), 687),
                ],
                start=180,
                end=0,
                fill=(168, 29, 91),
                width=6,
            )
            draw.ellipse(
                (
                    STEP * 2 + STEP * (int(event["starts"]) - START_DATE) - 4,
                    673,
                    STEP * 2 + STEP * (int(event["starts"]) - START_DATE) + 4,
                    683,
                ),
                fill=(240, 230, 168),
            )
    img.save("family_timeline.png")

    # function draws semicircles to indicate husband life events
    for event in other_ev_hp:
        if MARRIAGE is not None:
            if int(event["starts"]) < int(MARRIAGE["starts"]) or (
                int(MARRIAGE["ends"]) != 0
                and int(event["starts"]) > int(MARRIAGE["ends"])
            ):
                draw.arc(
                    [
                        (
                            (
                                STEP * 2
                                + STEP * (int(event["starts"]) - START_DATE)
                                - 10
                            ),
                            670,
                        ),
                        (
                            (
                                STEP * 2
                                + STEP * (int(event["starts"]) - START_DATE)
                                + 10
                            ),
                            688,
                        ),
                    ],
                    start=0,
                    end=180,
                    fill=(97, 27, 140, 99),
                    width=6,
                )
                draw.ellipse(
                    (
                        STEP * 2 + STEP * (int(event["starts"]) - START_DATE) - 4,
                        674,
                        STEP * 2 + STEP * (int(event["starts"]) - START_DATE) + 4,
                        684,
                    ),
                    fill=(240, 230, 168),
                )
            else:
                draw.arc(
                    [
                        (
                            (
                                STEP * 2
                                + STEP * (int(event["starts"]) - START_DATE)
                                - 10
                            ),
                            670,
                        ),
                        (
                            (
                                STEP * 2
                                + STEP * (int(event["starts"]) - START_DATE)
                                + 10
                            ),
                            688,
                        ),
                    ],
                    start=0,
                    end=180,
                    fill=(97, 27, 140),
                    width=6,
                )
                draw.ellipse(
                    (
                        STEP * 2 + STEP * (int(event["starts"]) - START_DATE) - 4,
                        674,
                        STEP * 2 + STEP * (int(event["starts"]) - START_DATE) + 4,
                        684,
                    ),
                    fill=(240, 230, 168),
                )
        else:
            draw.arc(
                [
                    ((STEP * 2 + STEP * (int(event["starts"]) - START_DATE) - 10), 670),
                    ((STEP * 2 + STEP * (int(event["starts"]) - START_DATE) + 10), 688),
                ],
                start=0,
                end=180,
                fill=(97, 27, 140),
                width=6,
            )
            draw.ellipse(
                (
                    STEP * 2 + STEP * (int(event["starts"]) - START_DATE) - 4,
                    674,
                    STEP * 2 + STEP * (int(event["starts"]) - START_DATE) + 4,
                    684,
                ),
                fill=(240, 230, 168),
            )
    img.save("family_timeline.png")

    # function draws dots to indicate family life events
    for event in other_ev_fp:
        if MARRIAGE is not None:
            if int(event["starts"]) < int(MARRIAGE["starts"]) or (
                int(MARRIAGE["ends"]) != 0
                and int(event["starts"]) > int(MARRIAGE["ends"])
            ):
                draw.ellipse(
                    (
                        STEP * 2 + STEP * (int(event["starts"]) - START_DATE) - 11,
                        667,
                        STEP * 2 + STEP * (int(event["starts"]) - START_DATE) + 11,
                        690,
                    ),
                    fill=(107, 24, 93, 99),
                    width=6,
                )
                draw.ellipse(
                    (
                        STEP * 2 + STEP * (int(event["starts"]) - START_DATE) - 4,
                        674,
                        STEP * 2 + STEP * (int(event["starts"]) - START_DATE) + 4,
                        683,
                    ),
                    fill=(240, 230, 168),
                )
            else:
                draw.ellipse(
                    (
                        STEP * 2 + STEP * (int(event["starts"]) - START_DATE) - 10,
                        668,
                        STEP * 2 + STEP * (int(event["starts"]) - START_DATE) + 10,
                        689,
                    ),
                    fill=(107, 24, 93),
                    outline=(240, 230, 168),
                )
                draw.ellipse(
                    (
                        STEP * 2 + STEP * (int(event["starts"]) - START_DATE) - 4,
                        674,
                        STEP * 2 + STEP * (int(event["starts"]) - START_DATE) + 4,
                        683,
                    ),
                    fill=(240, 230, 168),
                    outline=(240, 230, 168),
                )
        else:
            draw.ellipse(
                (
                    STEP * 2 + STEP * (int(event["starts"]) - START_DATE) - 10,
                    668,
                    STEP * 2 + STEP * (int(event["starts"]) - START_DATE) + 10,
                    689,
                ),
                fill=(107, 24, 93),
                outline=(240, 230, 168),
            )
            draw.ellipse(
                (
                    STEP * 2 + STEP * (int(event["starts"]) - START_DATE) - 4,
                    674,
                    STEP * 2 + STEP * (int(event["starts"]) - START_DATE) + 4,
                    683,
                ),
                fill=(240, 230, 168),
                outline=(240, 230, 168),
            )
    img.save("family_timeline.png")


# function draws semicircles to indicate life events
def draw_event_dots(w_ev):
    other_ev_wp = get_other_ev_wp(w_ev)
    other_ev_fp = []

    for event in w_ev:
        if (event["event_type"] == "04" and event["event_extent"] == "02") or (
            event["event_type"] == "04"
            and event["event_extent"] == "01"
            and event["event_pers_id"] != W_ID
        ):
            other_ev_fp.append(event)

    other_ev_wt = other_ev_wp + other_ev_fp
    other_ev_wt = sorted(
        other_ev_wt, reverse=True, key=lambda other_ev_wt: other_ev_wt["starts"]
    )

    # write event title
    j = 0
    while j < len(other_ev_wt):
        i = 0
        while (i < 7) and (j < len(other_ev_wt)):
            draw.line(
                (
                    (STEP * 2 + STEP * (int(other_ev_wt[j]["starts"]) - START_DATE)),
                    640 - (i * 18),
                    (
                        STEP * 2
                        + STEP * (int(other_ev_wt[j]["starts"]) - START_DATE)
                        + 6
                    ),
                    640 - (i * 18),
                ),
                fill=(107, 24, 93, 99),
                width=2,
            )
            draw.line(
                (
                    (STEP * 2 + STEP * (int(other_ev_wt[j]["starts"]) - START_DATE)),
                    640 - (i * 18),
                    (STEP * 2 + STEP * (int(other_ev_wt[j]["starts"]) - START_DATE)),
                    672,
                ),
                fill=(107, 24, 93, 80),
                width=2,
            )
            try:
                ev_pers = Person.get(other_ev_wt[j]["event_pers_id"])
                draw.text(
                    (
                        (
                            STEP * 2
                            + STEP * (int(other_ev_wt[j]["starts"]) - START_DATE)
                            + 7
                        ),
                        629 - (i * 18),
                    ),
                    f"{other_ev_wt[j]['starts']}  {ev_pers.f_name} {other_ev_wt[j]['descr']}",
                    font=font_reg,
                    fill=(107, 24, 93),
                )
            except UnboundLocalError:
                draw.text(
                    (
                        (
                            STEP * 2
                            + STEP * (int(other_ev_wt[j]["starts"]) - START_DATE)
                            + 7
                        ),
                        629 - (i * 18),
                    ),
                    f"{other_ev_wt[j]['starts']}  {other_ev_wt[j]['descr']}",
                    font=font_reg,
                    fill=(107, 24, 93),
                )
            j += 1
            i += 1

    img.save("family_timeline.png")

    # function draws semicircles to indicate wife life events
    for event in other_ev_wp:
        if MARRIAGE is not None:
            if int(event["starts"]) < int(MARRIAGE["starts"]) or int(
                event["starts"]
            ) > int(MARRIAGE["ends"]):
                draw.arc(
                    [
                        (
                            (
                                STEP * 2
                                + STEP * (int(event["starts"]) - START_DATE)
                                - 10
                            ),
                            669,
                        ),
                        (
                            (
                                STEP * 2
                                + STEP * (int(event["starts"]) - START_DATE)
                                + 10
                            ),
                            687,
                        ),
                    ],
                    start=180,
                    end=0,
                    fill=(168, 29, 91, 99),
                    width=6,
                )
                draw.ellipse(
                    (
                        STEP * 2 + STEP * (int(event["starts"]) - START_DATE) - 4,
                        673,
                        STEP * 2 + STEP * (int(event["starts"]) - START_DATE) + 4,
                        683,
                    ),
                    fill=(240, 230, 168),
                )
        else:
            draw.arc(
                [
                    ((STEP * 2 + STEP * (int(event["starts"]) - START_DATE) - 10), 669),
                    ((STEP * 2 + STEP * (int(event["starts"]) - START_DATE) + 10), 687),
                ],
                start=180,
                end=0,
                fill=(168, 29, 91),
                width=6,
            )
            draw.ellipse(
                (
                    STEP * 2 + STEP * (int(event["starts"]) - START_DATE) - 4,
                    673,
                    STEP * 2 + STEP * (int(event["starts"]) - START_DATE) + 4,
                    683,
                ),
                fill=(240, 230, 168),
            )
    img.save("family_timeline.png")

    # function draws dots to indicate family life events
    for event in other_ev_fp:
        if MARRIAGE is not None:
            if int(event["starts"]) < int(MARRIAGE["starts"]) or int(
                event["starts"]
            ) > int(MARRIAGE["ends"]):
                draw.ellipse(
                    (
                        STEP * 2 + STEP * (int(event["starts"]) - START_DATE) - 10,
                        668,
                        STEP * 2 + STEP * (int(event["starts"]) - START_DATE) + 10,
                        689,
                    ),
                    fill=(107, 24, 93, 99),
                    width=6,
                )
                draw.ellipse(
                    (
                        STEP * 2 + STEP * (int(event["starts"]) - START_DATE) - 4,
                        674,
                        STEP * 2 + STEP * (int(event["starts"]) - START_DATE) + 4,
                        683,
                    ),
                    fill=(240, 230, 168),
                )
        else:
            draw.ellipse(
                (
                    STEP * 2 + STEP * (int(event["starts"]) - START_DATE) - 10,
                    668,
                    STEP * 2 + STEP * (int(event["starts"]) - START_DATE) + 10,
                    689,
                ),
                fill=(107, 24, 93),
                outline=(240, 230, 168),
            )
            draw.ellipse(
                (
                    STEP * 2 + STEP * (int(event["starts"]) - START_DATE) - 4,
                    674,
                    STEP * 2 + STEP * (int(event["starts"]) - START_DATE) + 4,
                    683,
                ),
                fill=(240, 230, 168),
                outline=(240, 230, 168),
            )
    img.save("family_timeline.png")


# function returns the ordered list of dictionaries with children's info: whose children he is ("c" - common, "h" - husband's
# child from earlier marriage or "w" - wife's child from earlier marriages), what is his first and second name, when
# did he born and when did he die (if he is died), and dictionary with his life events


def ordered_child_list(h_child, w_child):
    children_list = []
    if h_child is not None and w_child is not None:
        kids = list(set(h_child + w_child))
        for kid in kids:
            kid = Person.get(kid)
            if kid.id in h_child and kid.id in w_child:
                children_list.append(
                    {
                        "whose": "c",
                        "f_name": kid.f_name,
                        "s_name": kid.s_name,
                        "born": kid.born,
                        "died": kid.died,
                        "events": kid.events,
                        "children2": kid.children,
                    }
                )
            elif kid.id in h_child and kid.id not in w_child:
                children_list.append(
                    {
                        "whose": "h",
                        "f_name": kid.f_name,
                        "s_name": kid.s_name,
                        "born": kid.born,
                        "died": kid.died,
                        "events": kid.events,
                        "children2": kid.children,
                    }
                )
            else:
                children_list.append(
                    {
                        "whose": "w",
                        "f_name": kid.f_name,
                        "s_name": kid.s_name,
                        "born": kid.born,
                        "died": kid.died,
                        "events": kid.events,
                        "children2": kid.children,
                    }
                )
    elif h_child is not None:
        kids = list(set(h_child))
        for kid in kids:
            kid = Person.get(kid)
            children_list.append(
                {
                    "whose": "h",
                    "f_name": kid.f_name,
                    "s_name": kid.s_name,
                    "born": kid.born,
                    "died": kid.died,
                    "events": kid.events,
                    "children2": kid.children,
                }
            )
    elif w_child is not None:
        kids = list(set(w_child))
        for kid in kids:
            kid = Person.get(kid)
            children_list.append(
                {
                    "whose": "w",
                    "f_name": kid.f_name,
                    "s_name": kid.s_name,
                    "born": kid.born,
                    "died": kid.died,
                    "events": kid.events,
                    "children2": kid.children,
                }
            )
    else:
        return children_list

    children_list = sorted(
        children_list, reverse=True, key=lambda children_list: children_list["born"]
    )

    return children_list


# function draws children life lines and events dots
def draw_ch_lifelines(ch):
    for child in ch:
        if child["whose"] == "w":
            global W_CH_NUM
            W_CH_NUM += 1
        elif child["whose"] == "h":
            global H_CH_NUM
            H_CH_NUM += 1
        else:
            global C_CH_NUM
            C_CH_NUM += 1

    w_ch = []
    h_ch = []
    if C_CH_NUM > 0:
        append_w_ch = round((W_CH_NUM + H_CH_NUM + C_CH_NUM) / 2) - W_CH_NUM
        append_h_ch = math.floor((W_CH_NUM + H_CH_NUM + C_CH_NUM) / 2) - H_CH_NUM
    else:
        append_w_ch = 0
        append_h_ch = 0

    last_ch = 1

    for _ in range(len(ch)):
        if ch[0]["whose"] == "h":
            h_ch.append(ch[0])
            ch.remove(ch[0])
            last_ch = 1
        elif ch[0]["whose"] == "w":
            w_ch.append(ch[0])
            ch.remove(ch[0])
            last_ch = 0
        else:
            if last_ch == 1:
                if append_w_ch > 0:
                    w_ch.append(ch[0])
                    ch.remove(ch[0])
                    last_ch = 0
                    append_w_ch -= 1
                else:
                    h_ch.append(ch[0])
                    ch.remove(ch[0])
                    last_ch = 1
                    append_h_ch -= 1
            else:
                if append_h_ch > 0:
                    h_ch.append(ch[0])
                    ch.remove(ch[0])
                    last_ch = 1
                    append_h_ch -= 1
                else:
                    w_ch.append(ch[0])
                    ch.remove(ch[0])
                    last_ch = 0
                    append_w_ch -= 1

    # distance betveen two life-lines
    if len(w_ch) > 0:
        w_lines_dist = 360 / len(w_ch)
    else:
        w_lines_dist = 50
    if len(h_ch) > 0:
        h_lines_dist = 360 / len(h_ch)
    else:
        h_lines_dist = 50

    for i in range(len(w_ch)):
        try:
            draw.line(
                (
                    STEP * 2 + STEP * (int(w_ch[i]["born"]) - START_DATE),
                    672,
                    STEP * 2 + STEP * (int(w_ch[i]["born"]) - START_DATE),
                    500 - i * w_lines_dist,
                ),
                fill=(168, 29, 91, 99),
                width=3,
            )
            if w_ch[i]["died"] is not None:
                draw.line(
                    (
                        STEP * 2 + STEP * (int(w_ch[i]["born"]) - START_DATE),
                        500 - i * w_lines_dist,
                        STEP * 2 + STEP * (int(w_ch[i]["died"]) - START_DATE),
                        500 - i * w_lines_dist,
                    ),
                    fill=(168, 29, 91),
                    width=4,
                )
                draw.ellipse(
                    (
                        STEP * 2 + STEP * (int(w_ch[i]["born"]) - START_DATE) - 10,
                        490 - i * w_lines_dist,
                        STEP * 2 + STEP * (int(w_ch[i]["born"]) - START_DATE) + 10,
                        510 - i * w_lines_dist,
                    ),
                    fill=(107, 24, 93),
                    outline=(240, 230, 168),
                )
                draw.ellipse(
                    (
                        STEP * 2 + STEP * (int(w_ch[i]["born"]) - START_DATE) - 4,
                        496 - i * w_lines_dist,
                        STEP * 2 + STEP * (int(w_ch[i]["born"]) - START_DATE) + 4,
                        504 - i * w_lines_dist,
                    ),
                    fill=(240, 230, 168),
                    outline=(240, 230, 168),
                )
                draw.ellipse(
                    (
                        STEP * 2 + STEP * (int(w_ch[i]["died"]) - START_DATE) - 8,
                        492 - i * w_lines_dist,
                        STEP * 2 + STEP * (int(w_ch[i]["died"]) - START_DATE) + 8,
                        508 - i * w_lines_dist,
                    ),
                    fill=(107, 24, 93),
                )
                draw.text(
                    (
                        (STEP * 2 + STEP * (int(w_ch[i]["died"]) - START_DATE) + 15),
                        490 - i * w_lines_dist,
                    ),
                    f"{w_ch[i]['died']}  died {w_ch[i]['f_name']} {w_ch[i]['s_name']}",
                    font=font_reg,
                    fill=(107, 24, 93),
                )
            else:
                draw.line(
                    (
                        STEP * 2 + STEP * (int(w_ch[i]["born"]) - START_DATE),
                        500 - i * w_lines_dist,
                        STEP * 2 + STEP * (NOW - START_DATE),
                        500 - i * w_lines_dist,
                    ),
                    fill=(168, 29, 91),
                    width=3,
                )
                draw.line(
                    (
                        STEP * 2 + STEP * (NOW - START_DATE),
                        500 - i * w_lines_dist,
                        2900,
                        500 - i * w_lines_dist,
                    ),
                    fill=(168, 29, 91, 99),
                    width=3,
                )

            draw.ellipse(
                (
                    STEP * 2 + STEP * (int(w_ch[i]["born"]) - START_DATE) - 10,
                    490 - i * w_lines_dist,
                    STEP * 2 + STEP * (int(w_ch[i]["born"]) - START_DATE) + 10,
                    510 - i * w_lines_dist,
                ),
                fill=(107, 24, 93),
                outline=(240, 230, 168),
            )
            draw.ellipse(
                (
                    STEP * 2 + STEP * (int(w_ch[i]["born"]) - START_DATE) - 4,
                    496 - i * w_lines_dist,
                    STEP * 2 + STEP * (int(w_ch[i]["born"]) - START_DATE) + 4,
                    504 - i * w_lines_dist,
                ),
                fill=(240, 230, 168),
                outline=(240, 230, 168),
            )
            draw.text(
                (
                    (STEP * 2 + STEP * (int(w_ch[i]["born"]) - START_DATE) + 7),
                    470 - i * w_lines_dist,
                ),
                f"{w_ch[i]['born']}  was born {w_ch[i]['f_name']}",
                font=font_reg,
                fill=(107, 24, 93),
            )
        except Exception:
            break

        if w_ch[i]["events"] is not None:
            marri = []
            for ev in w_ch[i]["events"]:
                if ev["event_type"] == "03":
                    marri.append(ev)

        if len(marri) > 0:
            for m in range(len(marri)):
                draw.ellipse(
                    (
                        STEP * 2 + STEP * (int(marri[m]["starts"]) - START_DATE) - 11,
                        489 - i * w_lines_dist,
                        STEP * 2 + STEP * (int(marri[m]["starts"]) - START_DATE) + 11,
                        511 - i * w_lines_dist,
                    ),
                    fill=(107, 24, 93),
                    outline=(240, 230, 168),
                )
                draw.ellipse(
                    (
                        STEP * 2 + STEP * (int(marri[m]["starts"]) - START_DATE) - 6,
                        494 - i * w_lines_dist,
                        STEP * 2 + STEP * (int(marri[m]["starts"]) - START_DATE) + 6,
                        506 - i * w_lines_dist,
                    ),
                    fill=(240, 230, 168),
                    outline=(240, 230, 168),
                )
                draw.ellipse(
                    (
                        STEP * 2 + STEP * (int(marri[m]["starts"]) - START_DATE) - 2,
                        498 - i * w_lines_dist,
                        STEP * 2 + STEP * (int(marri[m]["starts"]) - START_DATE) + 2,
                        502 - i * w_lines_dist,
                    ),
                    fill=(107, 24, 93),
                )

                try:
                    spouse = Person.get(marri[m]["event_pers_id"])
                    print_spouse = f"{spouse.f_name} {spouse.s_name}"
                except Exception:
                    print_spouse = "unknown person"

                draw.text(
                    (
                        (STEP * 2 + STEP * (int(marri[m]["starts"]) - START_DATE) + 7),
                        470 - (m * 20) - (i * w_lines_dist),
                    ),
                    f"{marri[m]['starts']}  got married {w_ch[i]['f_name']} {w_ch[i]['s_name']} ir {print_spouse}",
                    font=font_reg,
                    fill=(107, 24, 93),
                )

        if w_ch[i]["children2"] is not None:
            for chil in w_ch[i]["children2"]:
                grandch = Person.get(chil)
                draw.ellipse(
                    (
                        STEP * 2 + STEP * (int(grandch.born) - START_DATE) - 9,
                        491 - i * w_lines_dist,
                        STEP * 2 + STEP * (int(grandch.born) - START_DATE) + 9,
                        509 - i * w_lines_dist,
                    ),
                    fill=(107, 24, 93),
                    outline=(240, 230, 168),
                )
                draw.ellipse(
                    (
                        STEP * 2 + STEP * (int(grandch.born) - START_DATE) - 4,
                        496 - i * w_lines_dist,
                        STEP * 2 + STEP * (int(grandch.born) - START_DATE) + 4,
                        504 - i * w_lines_dist,
                    ),
                    fill=(240, 230, 168),
                    outline=(240, 230, 168),
                )

    for j in range(len(h_ch)):
        try:
            draw.line(
                (
                    STEP * 2 + STEP * (int(h_ch[j]["born"]) - START_DATE),
                    684,
                    STEP * 2 + STEP * (int(h_ch[j]["born"]) - START_DATE),
                    860 + j * h_lines_dist,
                ),
                fill=(168, 29, 91, 99),
                width=3,
            )
            if h_ch[j]["died"] is not None:
                draw.line(
                    (
                        STEP * 2 + STEP * (int(h_ch[j]["born"]) - START_DATE),
                        860 + j * h_lines_dist,
                        STEP * 2 + STEP * (int(h_ch[j]["died"]) - START_DATE),
                        860 + j * h_lines_dist,
                    ),
                    fill=(168, 29, 91),
                    width=4,
                )
                draw.ellipse(
                    (
                        STEP * 2 + STEP * (int(h_ch[j]["born"]) - START_DATE) - 10,
                        850 + j * h_lines_dist,
                        STEP * 2 + STEP * (int(h_ch[j]["born"]) - START_DATE) + 10,
                        870 + j * h_lines_dist,
                    ),
                    fill=(107, 24, 93),
                    outline=(240, 230, 168),
                )
                draw.ellipse(
                    (
                        STEP * 2 + STEP * (int(h_ch[j]["born"]) - START_DATE) - 4,
                        856 + j * h_lines_dist,
                        STEP * 2 + STEP * (int(h_ch[j]["born"]) - START_DATE) + 4,
                        864 + j * h_lines_dist,
                    ),
                    fill=(240, 230, 168),
                    outline=(240, 230, 168),
                )
                draw.ellipse(
                    (
                        STEP * 2 + STEP * (int(h_ch[j]["died"]) - START_DATE) - 8,
                        852 + j * h_lines_dist,
                        STEP * 2 + STEP * (int(h_ch[j]["died"]) - START_DATE) + 8,
                        868 + j * h_lines_dist,
                    ),
                    fill=(107, 24, 93),
                )
                draw.text(
                    (
                        (STEP * 2 + STEP * (int(h_ch[j]["died"]) - START_DATE) + 15),
                        850 + j * h_lines_dist,
                    ),
                    f"{h_ch[j]['died']}  died {h_ch[j]['f_name']} {h_ch[j]['s_name']}",
                    font=font_reg,
                    fill=(107, 24, 93),
                )
            else:
                draw.line(
                    (
                        STEP * 2 + STEP * (int(h_ch[j]["born"]) - START_DATE),
                        860 + j * h_lines_dist,
                        STEP * 2 + STEP * (NOW - START_DATE),
                        860 + j * h_lines_dist,
                    ),
                    fill=(168, 29, 91),
                    width=3,
                )
                draw.line(
                    (
                        STEP * 2 + STEP * (NOW - START_DATE),
                        860 + j * h_lines_dist,
                        2900,
                        860 + j * h_lines_dist,
                    ),
                    fill=(168, 29, 91, 99),
                    width=3,
                )
        except Exception:
            break

        draw.ellipse(
            (
                STEP * 2 + STEP * (int(h_ch[j]["born"]) - START_DATE) - 10,
                850 + j * h_lines_dist,
                STEP * 2 + STEP * (int(h_ch[j]["born"]) - START_DATE) + 10,
                870 + j * h_lines_dist,
            ),
            fill=(107, 24, 93),
            outline=(240, 230, 168),
        )
        draw.ellipse(
            (
                STEP * 2 + STEP * (int(h_ch[j]["born"]) - START_DATE) - 4,
                856 + j * h_lines_dist,
                STEP * 2 + STEP * (int(h_ch[j]["born"]) - START_DATE) + 4,
                864 + j * h_lines_dist,
            ),
            fill=(240, 230, 168),
            outline=(240, 230, 168),
        )
        draw.text(
            (
                (STEP * 2 + STEP * (int(h_ch[j]["born"]) - START_DATE) + 7),
                830 + j * h_lines_dist,
            ),
            f"{h_ch[j]['born']}  was born {h_ch[j]['f_name']}",
            font=font_reg,
            fill=(107, 24, 93),
        )

        if h_ch[j]["events"] is not None:
            mar = []
            for ev in h_ch[j]["events"]:
                if ev["event_type"] == "03":
                    mar.append(ev)

        if len(mar) > 0:
            for n in range(len(mar)):
                draw.ellipse(
                    (
                        STEP * 2 + STEP * (int(mar[n]["starts"]) - START_DATE) - 11,
                        849 + j * h_lines_dist,
                        STEP * 2 + STEP * (int(mar[n]["starts"]) - START_DATE) + 11,
                        871 + j * h_lines_dist,
                    ),
                    fill=(107, 24, 93),
                    outline=(240, 230, 168),
                )
                draw.ellipse(
                    (
                        STEP * 2 + STEP * (int(mar[n]["starts"]) - START_DATE) - 6,
                        854 + j * h_lines_dist,
                        STEP * 2 + STEP * (int(mar[n]["starts"]) - START_DATE) + 6,
                        866 + j * h_lines_dist,
                    ),
                    fill=(240, 230, 168),
                    outline=(240, 230, 168),
                )
                draw.ellipse(
                    (
                        STEP * 2 + STEP * (int(mar[n]["starts"]) - START_DATE) - 2,
                        858 + j * h_lines_dist,
                        STEP * 2 + STEP * (int(mar[n]["starts"]) - START_DATE) + 2,
                        862 + j * h_lines_dist,
                    ),
                    fill=(107, 24, 93),
                )

                try:
                    spouse = Person.get(mar[n]["event_pers_id"])
                    print_spouse = f"{spouse.f_name} {spouse.s_name}"
                except Exception:
                    print_spouse = "unknown person"
                draw.text(
                    (
                        (STEP * 2 + STEP * (int(mar[n]["starts"]) - START_DATE) + 7),
                        830 + (n * 35) + (j * h_lines_dist),
                    ),
                    f"{ev['starts']}  got married {h_ch[j]['f_name']} {h_ch[j]['s_name']} ir {print_spouse}",
                    font=font_reg,
                    fill=(107, 24, 93),
                )

        if h_ch[j]["children2"] is not None:
            for chil in h_ch[j]["children2"]:
                grandch = Person.get(chil)
                draw.ellipse(
                    (
                        STEP * 2 + STEP * (int(grandch.born) - START_DATE) - 9,
                        851 + j * h_lines_dist,
                        STEP * 2 + STEP * (int(grandch.born) - START_DATE) + 9,
                        869 + j * h_lines_dist,
                    ),
                    fill=(107, 24, 93),
                    outline=(240, 230, 168),
                )
                draw.ellipse(
                    (
                        STEP * 2 + STEP * (int(grandch.born) - START_DATE) - 4,
                        856 + j * h_lines_dist,
                        STEP * 2 + STEP * (int(grandch.born) - START_DATE) + 4,
                        864 + j * h_lines_dist,
                    ),
                    fill=(240, 230, 168),
                    outline=(240, 230, 168),
                )


if __name__ == "__main__":
    main()
