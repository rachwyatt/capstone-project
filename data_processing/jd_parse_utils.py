import pandas as pd


def load_skill_dict(path='skillsets.csv'):
    skills = pd.read_csv(path)
    skills['Skills'] = skills['Skills'].str.lower()
    skills['Category'] = skills['Category'].str.lower()
    skills_dict = skills.set_index('Skills').to_dict()
    skills_dict = skills_dict['Category']
    return skills_dict


def get_skills(text):
    import regex as ree

    skills_dict = load_skill_dict()
    skills_ls = list(skills_dict.keys())

    p1 = ree.compile(r" \L<words> ", words=skills_ls)
    p2 = ree.compile(r"\t\L<words> ", words=skills_ls)
    p3 = ree.compile(r",\L<words> ", words=skills_ls)
    p4 = ree.compile(r" \L<words>,", words=skills_ls)
    p5 = ree.compile(r" \L<words>\.", words=skills_ls)
    p6 = ree.compile(r" \L<words>\n", words=skills_ls)
    p7 = ree.compile(r" \L<words>/", words=skills_ls)
    p8 = ree.compile(r"/\L<words>", words=skills_ls)
    p9 = ree.compile(r"\(\L<words>", words=skills_ls)
    p10 = ree.compile(r" \L<words>\)", words=skills_ls)
    p11 = ree.compile(r"\n\L<words>", words=skills_ls)
    patterns = [p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11]

    found_skills = []
    for p in patterns:
        found_skills += p.findall(text.lower())

    found_skills = [x.strip(' ,\.\t\n/)(') for x in found_skills]

    # get the unique skills
    found_skills = sorted(list(set(found_skills)))
    return found_skills


def get_skill_cat(skill_ls):
    cats = []
    skills_dict = load_skill_dict()
    skills_ls = list(skills_dict.keys())

    for sk in skill_ls:
        try:
            cat = skills_dict[sk]
            cats.append(cat)
        except:
            cats.append(skills_dict['.net'])
    return cats


def degree_names():
    list_of_postdoc_names = (
        "Postdoc",
        "Postdoctoral Researcher",
        "Research Scientist"
    )

    list_of_phd_names = (
        "PhD",
        "Ph.D.",
        "Doctorate"
    )

    list_of_master_names = (
        "MSc",
        "Master ",
        "Masters",
        "M.Sc.",
        "M.S.",
        " MS,",
        " MS of ",
        " MS in ",
        " MA ",
        " MA,",
        "M.A.",
        "M.B.A.",
        " MBA ",
        "Master of ",
        "Post Graduate Diploma",
        "/MS/",
        "MS/",
    )

    list_of_bs_names = (
        "B.S.",
        " BS,"
        "B.S ",
        " BS ",
        "BS/",
        "/BS/",
        " BA ",
        "B.A.,",
        "B.A.-",
        "B.A. ",
        "Bachelor of Science",
        "Bachelor of"
        "B.Sc.",
        "Bachelor",
        "B.E. ",
        "B.E.,",
        "B.E.-",
        " BSE ",
        "Bachelor of Engineering",
        "B.Tech ",
        "B.Tech,",
        "B.Tech-"
    )

    return (list_of_postdoc_names,
            list_of_phd_names,
            list_of_master_names,
            list_of_bs_names)


def clean_deg(x, keyword='bachelor'):
    if len(x) > 0:
        return keyword
    else:
        return ""


def get_skill_education(jd):
    """
    extract education and skills requirements from the job description

    return education requirements and skills
    """
    import regex as ree

    jd = jd.lower()
    skills = get_skills(jd)
    # posdoc, phd, master, bs
    degree_list_of_lists = degree_names()
    found_items = []
    for ind, ls in enumerate(degree_list_of_lists):
        p = ree.compile(r"\L<words>", words=[kk.lower() for kk in ls])
        found = p.findall(jd)
        if len(found) > 1:
            if ind == 0:
                found_items.append('posdoc')
            elif ind == 1:
                found_items.append('phd')
            elif ind == 2:
                found_items.append('master')
            elif ind == 3:
                found_items.append('bs')

    education = ';'.join(found_items)
    skills = ', '.join(skills)

    return education, skills
