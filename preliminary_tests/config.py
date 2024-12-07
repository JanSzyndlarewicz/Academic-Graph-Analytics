import os

from dotenv import load_dotenv

load_dotenv()

SCOPUS_KEY = os.getenv("SCOPUS_KEY")
PAPER_SEARCH_URL = "https://api.elsevier.com/content/search/scopus"
SAFETY_LIMIT = 25

country2uni_institutions_names = {
    "Germany": [
        "Helmholtz Gemeinschaft",
        "Max Planck Gesellschaft",
        "European Molecular Biology Laboratory Heidelberg",
        "European Molecular Biology Organization",
        "Leibniz Gemeinschaft",
        "Technische Universitat Munchen",
        "Max Planck Institut fur Informatik",
        "Deutsches Krebsforschungszentrum",
        "Max Planck Institut fur Intelligente Systeme"
    ],
    "Poland": [
        "Polish Academy of Sciences",
        "Jagiellonian University",
        "University of Warsaw",
        "Mossakowski Medical Research Centre Polish Academy of Sciences",
        "Nicolaus Copernicus University",
        "Adam Mickiewicz University",
        "University of Lodz",
        "AGH University of Science and Technology",
        "Medical University of Warsaw",
        "Medical University of Lodz"
    ],
    "Russian Federation": [
        "Russian Academy of Sciences",
        "Lomonosov Moscow State University",
        "Saint Petersburg State University",
        "Institute of Chemical Biology and Fundamental Medicine Russian Academy of Sciences",
        "State University - Higher School of Economics",
        "Ministry of Science and Higher Education",
        "I.M. Sechenov First Moscow State Medical University",
        "Peter the Great St Petersburg Polytechnic University",
        "Shemyakin-Ovchinnikov Institute of Bioorganic Chemistry of the Russian Academy of Sciences",
        "Ural Federal University"
    ],
    "United Kingdom": [
        "University of Oxford",
        "University College London",
        "European Bioinformatics Institute EMBL",
        "University of Cambridge",
        "Imperial College London",
        "Kings College London",
        "Medical Research Council",
        "The University of Edinburgh",
        "The University of Manchester"
    ],
    "United States": [
        "Harvard University",
        "Harvard Medical School",
        "U.S. Department of Health & Human Services",
        "National Institutes of Health",
        "Stanford University",
        "American Cancer Society",
        "The New York Genome Center",
        "Johns Hopkins University",
        "Parker Institute for Cancer Immunotherapy",
        "Massachusetts Institute of Technology"
    ],
    "China": [
        "Chinese Academy of Sciences",
        "Ministry of Education of the People's Republic of China",
        "University of Chinese Academy of Sciences",
        "Tsinghua University",
        "Zhejiang University",
        "Shanghai Jiao Tong University",
        "Peking University",
        "State Grid Corporation of China",
        "Huazhong University of Science and Technology",
        "Sichuan University"
    ],
    "Switzerland": [
        "Ludwig Institute for Cancer Research Lausanne",
        "Swiss Federal Institute of Technology",
        "IBM Switzerland",
        "Universitat Zurich",
        "Ecole Polytechnique Federale de Lausanne",
        "Novartis Institutes for Biomedical Research, Switzerland",
        "Swiss Institute of Bioinformatics",
        "Universitat Bern",
        "Hoffmann-La Roche Ltd, Switzerland",
        "Universite de Geneve"
    ]
}

country2unis_names = {
    "Russian Federation": [
        "Lomonosov Moscow State University",
        "Saint Petersburg State University",
        "Krasnoyarsk State Agrarian University",
        "State University - Higher School of Economics",
        "Peter the Great St Petersburg Polytechnic University",
        "Saint Petersburg State University of Architecture and Civil Engineering",
        "Ural Federal University",
        "Peoples' Friendship University of Russia",
        "Saint Petersburg Mining University",
        "Moscow State University of Civil Engineering"
    ],
    "United Kingdom": [
        "University of Oxford",
        "University College London",
        "University of Cambridge",
        "Imperial College London",
        "The University of Edinburgh",
        "The University of Manchester",
        "Kings College London",
        "University of Liverpool",
        "University of Bristol",
        "University of Nottingham"
    ],
    "United States": [
        "Harvard University",
        "Harvard Medical School",
        "Stanford University",
        "Johns Hopkins University",
        "University of Pennsylvania",
        "University of Michigan, Ann Arbor",
        "University of Chicago",
        "University of Washington",
        "Columbia University",
        "Massachusetts Institute of Technology"
    ],
    "Switzerland": [
        "Swiss Federal Institute of Technology",
        "Universitat Zurich",
        "Ecole Polytechnique Federale de Lausanne",
        "Universitat Bern",
        "Universite de Geneve",
        "Universitat Basel",
        "Universite de Lausanne",
        "Universita della Svizzera Italiana",
        "Universite de Fribourg",
        "Universitat St Gallen"
    ],
    "Poland": [
        "Jagiellonian University",
        "University of Warsaw",
        "Nicolaus Copernicus University",
        "University of Lodz",
        "Adam Mickiewicz University",
        "AGH University of Science and Technology",
        "Warsaw University of Life Sciences",
        "Wroclaw Medical University",
        "University of Warmia and Mazury",
        "Poznan University of Life Sciences"
    ],
    "Germany": [
        "Hochschule fur Wirtschaft und Recht Berlin",
        "Technische Universitat Munchen",
        "Ludwig-Maximilians Universitat Munchen",
        "Universitat Hamburg",
        "Universitat Heidelberg",
        "Friedrich-Alexander-Universitat Erlangen-Nurnberg",
        "Rheinisch-Westfalische Technische Hochschule Aachen",
        "Technische Universitat Dresden",
        "Rheinische Friedrich-Wilhelms-Universitat Bonn",
        "Karlsruher Institut fur Technologie"
    ],
    "China": [
        "University of Chinese Academy of Sciences",
        "Tsinghua University",
        "Zhejiang University",
        "Shanghai Jiao Tong University",
        "Peking University",
        "Huazhong University of Science and Technology",
        "Sichuan University",
        "Central South University",
        "Sun Yat-Sen University",
        "Fudan University"
    ]
}
