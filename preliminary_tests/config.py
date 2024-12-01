import os

from dotenv import load_dotenv

load_dotenv()

SCOPUS_KEY = os.getenv('SCOPUS_KEY')
PAPER_SEARCH_URL = 'https://api.elsevier.com/content/search/scopus'
SAFETY_LIMIT = 25


top_universities_by_country = {
    "United States": [
        "Harvard University", 
        "Massachusetts Institute of Technology (MIT)", 
        "Stanford University", 
        "California Institute of Technology (Caltech)", 
        "University of Chicago", 
        "Princeton University", 
        "Columbia University", 
        "Yale University", 
        "University of California, Berkeley", 
        "University of California, Los Angeles (UCLA)"
    ],
    "United Kingdom": [
        "University of Oxford", 
        "University of Cambridge", 
        "Imperial College London", 
        "London School of Economics and Political Science (LSE)", 
        "University College London (UCL)", 
        "University of Edinburgh", 
        "King's College London", 
        "University of Manchester", 
        "University of Warwick", 
        "University of Bristol"
    ],
    "Germany": [
        "Ludwig Maximilian University of Munich", 
        "Technical University of Munich", 
        "Heidelberg University", 
        "Humboldt University of Berlin", 
        "University of Freiburg", 
        "RWTH Aachen University", 
        "University of Göttingen", 
        "University of Mannheim", 
        "University of Stuttgart", 
        "University of Leipzig"
    ],
    "France": [
        "Université PSL (Paris Sciences et Lettres)", 
        "Sorbonne University", 
        "École Normale Supérieure", 
        "École Polytechnique", 
        "Université de Paris", 
        "Sciences Po", 
        "Université Grenoble Alpes", 
        "Université Paris-Saclay", 
        "Université de Lyon", 
        "Université de Strasbourg"
    ],
    "China": [
        "Tsinghua University", 
        "Peking University", 
        "Fudan University", 
        "Shanghai Jiao Tong University", 
        "Zhejiang University", 
        "University of Science and Technology of China", 
        "Beijing Normal University", 
        "Xi'an Jiaotong University", 
        "Renmin University of China", 
        "Nanjing University"
    ],
    "Canada": [
        "University of Toronto", 
        "McGill University", 
        "University of British Columbia", 
        "University of Montreal", 
        "McMaster University", 
        "University of Alberta", 
        "University of Waterloo", 
        "Western University", 
        "University of Calgary", 
        "Queen's University"
    ],
    "Japan": [
        "University of Tokyo", 
        "Kyoto University", 
        "Osaka University", 
        "Tohoku University", 
        "Keio University", 
        "Hitotsubashi University", 
        "Nagoya University", 
        "Hokkaido University", 
        "Waseda University", 
        "Chuo University"
    ],
    "Australia": [
        "Australian National University", 
        "University of Melbourne", 
        "University of Sydney", 
        "University of Queensland", 
        "University of New South Wales", 
        "University of Western Australia", 
        "University of Adelaide", 
        "University of Technology Sydney", 
        "Monash University", 
        "University of Tasmania"
    ],
    "Switzerland": [
        "ETH Zurich", 
        "École Polytechnique Fédérale de Lausanne (EPFL)", 
        "University of Zurich", 
        "University of Geneva", 
        "University of Basel", 
        "University of St. Gallen", 
        "University of Bern", 
        "Zurich University of the Arts", 
        "University of Lucerne", 
        "Swiss Federal Institute of Technology in Lausanne"
    ],
    "Netherlands": [
        "University of Amsterdam", 
        "Delft University of Technology", 
        "Leiden University", 
        "Utrecht University", 
        "Vrije Universiteit Amsterdam", 
        "Eindhoven University of Technology", 
        "Radboud University", 
        "Groningen University", 
        "Wageningen University", 
        "Maastricht University"
    ],
    "Sweden": [
        "Karolinska Institute", 
        "Lund University", 
        "Stockholm University", 
        "Uppsala University", 
        "Chalmers University of Technology", 
        "KTH Royal Institute of Technology", 
        "Umeå University", 
        "Linköping University", 
        "Göteborg University", 
        "Swedish University of Agricultural Sciences"
    ],
    "South Korea": [
        "Seoul National University", 
        "KAIST (Korea Advanced Institute of Science and Technology)", 
        "POSTECH (Pohang University of Science and Technology)", 
        "Yonsei University", 
        "Korea University", 
        "Sungkyunkwan University", 
        "Hanyang University", 
        "Ewha Womans University", 
        "Pusan National University", 
        "Chung-Ang University"
    ],
    "Finland": [
        "University of Helsinki", 
        "Aalto University", 
        "University of Turku", 
        "University of Oulu", 
        "University of Eastern Finland", 
        "Tampere University", 
        "Lappeenranta-Lahti University of Technology", 
        "University of Jyväskylä", 
        "University of Lapland", 
        "Hanken School of Economics"
    ],
    "Singapore": [
        "National University of Singapore", 
        "Nanyang Technological University", 
        "Singapore Management University", 
        "Singapore University of Technology and Design", 
        "Yale-NUS College", 
        "Duke-NUS Medical School", 
        "Lee Kong Chian School of Business", 
        "SUTD (Singapore University of Technology and Design)", 
        "SIT (Singapore Institute of Technology)", 
        "SIM University"
    ],
    "Denmark": [
        "University of Copenhagen", 
        "Aarhus University", 
        "Technical University of Denmark", 
        "Copenhagen Business School", 
        "Aalborg University", 
        "University of Southern Denmark", 
        "Roskilde University", 
        "IT University of Copenhagen", 
        "University of Roskilde", 
        "University of Aarhus"
    ],
    "Belgium": [
        "KU Leuven", 
        "Université Catholique de Louvain (UCLouvain)", 
        "Université Libre de Bruxelles (ULB)", 
        "Ghent University", 
        "Vrije Universiteit Brussel (VUB)", 
        "Université de Liège", 
        "Université de Namur", 
        "Antwerp University", 
        "Hasselt University", 
        "University of Leuven"
    ],
    "Israel": [
        "Hebrew University of Jerusalem", 
        "Tel Aviv University", 
        "Weizmann Institute of Science", 
        "Technion - Israel Institute of Technology", 
        "University of Haifa", 
        "Ben-Gurion University of the Negev", 
        "Bar-Ilan University", 
        "IDC Herzliya", 
        "Ariel University", 
        "Open University of Israel"
    ],
    "India": [
        "Indian Institute of Science", 
        "Indian Institutes of Technology (IIT) Bombay", 
        "Indian Institutes of Technology (IIT) Delhi", 
        "Indian Institutes of Technology (IIT) Madras", 
        "Indian Institutes of Technology (IIT) Kanpur", 
        "Indian Institutes of Technology (IIT) Kharagpur", 
        "University of Delhi", 
        "Jawaharlal Nehru University", 
        "University of Mumbai", 
        "Banaras Hindu University"
    ],
    "Italy": [
        "University of Bologna", 
        "Sapienza University of Rome", 
        "Politecnico di Milano", 
        "University of Milan", 
        "University of Padua", 
        "University of Florence", 
        "University of Turin", 
        "University of Naples Federico II", 
        "University of Pisa", 
        "Scuola Normale Superiore di Pisa"
    ],
    "Spain": [
        "University of Barcelona", 
        "Autonomous University of Madrid", 
        "University of Madrid", 
        "Pompeu Fabra University", 
        "University of Valencia", 
        "Complutense University of Madrid", 
        "University of Seville", 
        "University of Zaragoza", 
        "University of Granada", 
        "University of Salamanca"
    ],
    "Russia": [
        "Lomonosov Moscow State University", 
        "Saint Petersburg State University", 
        "Novosibirsk State University", 
        "Tomsk State University", 
        "Moscow Institute of Physics and Technology", 
        "Moscow State Technical University of Civil Aviation", 
        "Bauman Moscow State Technical University", 
        "Higher School of Economics", 
        "Kazan Federal University", 
        "Russian Academy of Sciences"
    ],
    "Poland": [
        "University of Warsaw", 
        "Jagiellonian University", 
        "Warsaw University of Technology", 
        "Adam Mickiewicz University", 
        "AGH University of Science and Technology", 
        "Wrocław University of Science and Technology", 
        "University of Gdańsk", 
        "University of Łódź", 
        "University of Silesia", 
        "Nicolaus Copernicus University"
    ]
}
