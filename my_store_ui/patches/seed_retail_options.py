"""Seed the admin-managed dropdown options.

Every Sri Lankan city the Customer form's City picker offers, plus the Business
Nature and Transport Method choices the form used to hard-code, and starting
Carpet Category / Product Size / Product Material lists.

Idempotent and non-destructive: an option that already exists is left exactly as
the admin left it (including a deactivated one), and options the admin added
themselves are never removed.
"""

from __future__ import annotations

import frappe

# Districts run north to south so the seeded ordering is at least geographic.
CITIES = (
	# Western Province -- Colombo
	"Colombo", "Sri Jayawardenepura Kotte", "Dehiwala-Mount Lavinia", "Moratuwa", "Ratmalana",
	"Kolonnawa", "Kaduwela", "Maharagama", "Kesbewa", "Homagama", "Padukka", "Hanwella",
	"Avissawella", "Battaramulla", "Nugegoda", "Rajagiriya", "Piliyandala", "Boralesgamuwa",
	"Kottawa", "Athurugiriya", "Malabe", "Kotikawatta", "Mulleriyawa", "Angoda", "Wellampitiya",
	"Kohuwala", "Nawala", "Thalawathugoda", "Pannipitiya", "Hokandara", "Kalubowila",
	# Western Province -- Gampaha
	"Gampaha", "Negombo", "Wattala", "Ja-Ela", "Kelaniya", "Peliyagoda", "Kadawatha", "Ragama",
	"Kandana", "Seeduwa", "Katunayake", "Minuwangoda", "Divulapitiya", "Mirigama", "Nittambuwa",
	"Veyangoda", "Attanagalla", "Dompe", "Biyagama", "Kiribathgoda", "Mahara", "Yakkala",
	"Ekala", "Ganemulla", "Weliweriya", "Delgoda", "Pugoda", "Kirindiwela",
	# Western Province -- Kalutara
	"Kalutara", "Panadura", "Horana", "Beruwala", "Aluthgama", "Bandaragama", "Matugama",
	"Wadduwa", "Ingiriya", "Bulathsinhala", "Dodangoda", "Agalawatta", "Millaniya",
	"Madurawala", "Payagala", "Maggona",
	# Central Province -- Kandy
	"Kandy", "Peradeniya", "Katugastota", "Gampola", "Nawalapitiya", "Akurana", "Digana",
	"Kundasale", "Pilimatalawa", "Kadugannawa", "Wattegama", "Teldeniya", "Galagedara",
	"Menikhinna", "Ampitiya", "Doluwa", "Ududumbara", "Panvila", "Hataraliyadda", "Poojapitiya",
	"Minipe", "Delthota",
	# Central Province -- Matale
	"Matale", "Dambulla", "Sigiriya", "Galewela", "Ukuwela", "Rattota", "Naula",
	"Palapathwela", "Yatawatta", "Laggala-Pallegama", "Wilgamuwa", "Pallepola",
	# Central Province -- Nuwara Eliya
	"Nuwara Eliya", "Hatton", "Talawakelle", "Ginigathena", "Kotagala", "Maskeliya", "Ragala",
	"Walapane", "Kotmale", "Ambewela", "Bogawantalawa", "Nanu Oya", "Pundaluoya",
	"Rikillagaskada", "Hanguranketha",
	# Southern Province -- Galle
	"Galle", "Ambalangoda", "Hikkaduwa", "Elpitiya", "Baddegama", "Bentota", "Karapitiya",
	"Unawatuna", "Ahangama", "Habaraduwa", "Balapitiya", "Ahungalla", "Neluwa", "Nagoda",
	"Yakkalamulla", "Imaduwa", "Wanduramba", "Thawalama", "Udugama", "Karandeniya",
	# Southern Province -- Matara
	"Matara", "Weligama", "Mirissa", "Dikwella", "Akuressa", "Hakmana", "Deniyaya",
	"Kamburupitiya", "Devinuwara", "Kotapola", "Pitabeddara", "Morawaka", "Thihagoda",
	"Malimbada", "Athuraliya", "Welipitiya",
	# Southern Province -- Hambantota
	"Hambantota", "Tangalle", "Tissamaharama", "Ambalantota", "Beliatta", "Weeraketiya",
	"Kataragama", "Sooriyawewa", "Angunakolapelessa", "Lunugamvehera", "Walasmulla",
	"Middeniya", "Okewela", "Ranna",
	# Northern Province -- Jaffna
	"Jaffna", "Nallur", "Chavakachcheri", "Point Pedro", "Karainagar", "Velanai", "Kayts",
	"Tellippalai", "Kopay", "Sandilipay", "Uduvil", "Maruthankerny", "Delft", "Chankanai",
	"Manipay",
	# Northern Province -- Kilinochchi, Mannar, Vavuniya, Mullaitivu
	"Kilinochchi", "Pallai", "Poonakary", "Paranthan",
	"Mannar", "Nanattan", "Musali", "Madhu", "Pesalai", "Talaimannar",
	"Vavuniya", "Cheddikulam", "Nedunkeni", "Omanthai",
	"Mullaitivu", "Puthukkudiyiruppu", "Oddusuddan", "Thunukkai",
	# Eastern Province -- Trincomalee
	"Trincomalee", "Kinniya", "Mutur", "Kantale", "Nilaveli", "Kuchchaveli",
	"Thambalagamuwa", "Gomarankadawala", "Seruvila",
	# Eastern Province -- Batticaloa
	"Batticaloa", "Kattankudy", "Eravur", "Valaichchenai", "Kaluwanchikudy", "Oddamavadi",
	"Chenkalady", "Vakarai", "Arayampathy", "Kokkadichcholai",
	# Eastern Province -- Ampara
	"Ampara", "Kalmunai", "Akkaraipattu", "Sainthamaruthu", "Sammanthurai", "Pottuvil",
	"Addalaichenai", "Nintavur", "Uhana", "Mahaoya", "Damana", "Lahugala", "Karaitivu",
	"Dehiattakandiya",
	# North Western Province -- Kurunegala
	"Kurunegala", "Kuliyapitiya", "Narammala", "Pannala", "Wariyapola", "Nikaweratiya",
	"Melsiripura", "Ibbagamuwa", "Mawathagama", "Polgahawela", "Alawwa", "Giriulla",
	"Hettipola", "Galgamuwa", "Bingiriya", "Rideegama", "Dodangaslanda", "Kobeigane",
	"Mahawa", "Yapahuwa", "Ganewatta", "Bamunakotuwa", "Pothuhera",
	# North Western Province -- Puttalam
	"Puttalam", "Chilaw", "Wennappuwa", "Marawila", "Nattandiya", "Anamaduwa", "Dankotuwa",
	"Madampe", "Mundel", "Kalpitiya", "Norochcholai", "Arachchikattuwa", "Pallama",
	"Karuwalagaswewa", "Nawagattegama", "Vanathavilluwa",
	# North Central Province -- Anuradhapura
	"Anuradhapura", "Kekirawa", "Medawachchiya", "Thambuttegama", "Eppawala", "Mihintale",
	"Galenbindunuwewa", "Horowpothana", "Nochchiyagama", "Talawa", "Rambewa",
	"Kahatagasdigiliya", "Padaviya", "Galnewa", "Ipalogama", "Rajanganaya", "Thirappane",
	# North Central Province -- Polonnaruwa
	"Polonnaruwa", "Kaduruwela", "Hingurakgoda", "Medirigiriya", "Dimbulagala", "Welikanda",
	"Lankapura", "Elahera", "Minneriya", "Aralaganwila",
	# Uva Province -- Badulla
	"Badulla", "Bandarawela", "Haputale", "Welimada", "Diyatalawa", "Ella", "Passara",
	"Mahiyanganaya", "Hali-Ela", "Lunugala", "Meegahakiwula", "Kandaketiya",
	"Uva-Paranagama", "Rideemaliyadda", "Soranathota", "Haldummulla", "Girandurukotte",
	# Uva Province -- Monaragala
	"Monaragala", "Wellawaya", "Bibile", "Buttala", "Medagama", "Siyambalanduwa",
	"Thanamalvila", "Badalkumbura", "Madulla", "Sevanagala",
	# Sabaragamuwa Province -- Ratnapura
	"Ratnapura", "Embilipitiya", "Balangoda", "Pelmadulla", "Eheliyagoda", "Kuruwita",
	"Kalawana", "Kahawatta", "Godakawela", "Nivithigala", "Opanayaka", "Ayagama",
	"Weligepola", "Imbulpe", "Elapatha", "Kolonna", "Kiriella",
	# Sabaragamuwa Province -- Kegalle
	"Kegalle", "Mawanella", "Warakapola", "Rambukkana", "Galigamuwa", "Dehiowita",
	"Yatiyantota", "Ruwanwella", "Deraniyagala", "Bulathkohupitiya", "Aranayaka",
	"Kitulgala", "Hemmathagama", "Undugoda",
)

# The choices the forms used to hard-code, moved to the master so the admin owns them.
BUSINESS_NATURES = (
	"Retailer", "Wholesaler", "Department Store", "Contractor", "Hotel", "Office",
	"Distributor", "Other",
)
TRANSPORT_METHODS = (
	"Customer Pickup", "Company Delivery", "Own Vehicle", "Courier",
	"Third-Party Transport", "Other",
)

# Starting points for the carpet-only lists. Deliberately short: the admin adds
# what the business actually sells from the same page.
CARPET_CATEGORIES = (
	"Area Rug", "Wall-to-Wall", "Runner", "Door Mat", "Prayer Mat", "Shaggy",
	"Persian", "Outdoor",
)
PRODUCT_SIZES = (
	"2 x 3 ft", "3 x 5 ft", "4 x 6 ft", "5 x 8 ft", "6 x 9 ft", "8 x 10 ft", "9 x 12 ft",
	"Runner 2 x 8 ft", "Runner 2 x 12 ft",
)
PRODUCT_MATERIALS = (
	"Wool", "Cotton", "Silk", "Jute", "Viscose", "Polyester", "Polypropylene", "Nylon",
	"Blend",
)

SEED = (
	("City", CITIES),
	("Business Nature", BUSINESS_NATURES),
	("Transport Method", TRANSPORT_METHODS),
	("Carpet Category", CARPET_CATEGORIES),
	("Product Size", PRODUCT_SIZES),
	("Product Material", PRODUCT_MATERIALS),
)


def execute() -> None:
	if not frappe.db.exists("DocType", "Retail Option List"):
		return
	for option_type, values in SEED:
		existing = set(frappe.get_all(
			"Retail Option List", filters={"option_type": option_type}, pluck="option_value"))
		for index, value in enumerate(values):
			if value in existing:
				continue
			doc = frappe.new_doc("Retail Option List")
			doc.option_type = option_type
			doc.option_value = value
			doc.sort_order = index
			doc.is_active = 1
			doc.insert(ignore_permissions=True)
	frappe.db.commit()
