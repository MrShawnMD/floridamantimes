"""City -> county lookup for the Roach Report (DBPR files list city, not county).
Covers Tampa Bay, Sarasota/Manatee and Southwest/Central-West Florida (DBPR districts 3 and 7)."""

_C = {
    "Hillsborough": "Tampa, Brandon, Riverview, Plant City, Lithia, Lutz, Gibsonton, Valrico, Seffner, Apollo Beach, Ruskin, "
                    "Sun City Center, Wimauma, Thonotosassa, Dover, Temple Terrace, Odessa, Town N Country, Carrollwood, Westchase, "
                    "Fishhawk, Mango, Balm, Sun City",
    "Pinellas": "St Petersburg, Saint Petersburg, St Pete, St Pete Beach, Saint Pete Beach, Clearwater, Clearwater Beach, Largo, "
                "Dunedin, Gulfport, Pinellas Park, Seminole, Palm Harbor, Tarpon Springs, Safety Harbor, Oldsmar, Treasure Island, "
                "Madeira Beach, Indian Rocks Beach, Indian Shores, Kenneth City, Belleair, Belleair Bluffs, Redington Shores, "
                "Redington Beach, North Redington Beach, South Pasadena, Tierra Verde, Crystal Beach, Ozona",
    "Pasco": "New Port Richey, Port Richey, Holiday, Hudson, Wesley Chapel, Zephyrhills, Dade City, Land O Lakes, Trinity, "
             "San Antonio, Shady Hills, Bayonet Point",
    "Hernando": "Brooksville, Spring Hill, Weeki Wachee, Hernando Beach",
    "Citrus": "Crystal River, Inverness, Homosassa, Homosassa Springs, Lecanto, Beverly Hills, Hernando, Floral City",
    "Polk": "Lakeland, Winter Haven, Bartow, Davenport, Haines City, Auburndale, Lake Wales, Mulberry, Lake Alfred, Poinciana, "
            "Frostproof, Fort Meade, Eagle Lake, Dundee, Polk City, Babson Park",
    "Manatee": "Bradenton, Palmetto, Ellenton, Parrish, Holmes Beach, Bradenton Beach, Anna Maria, Lakewood Ranch, Cortez, "
               "Myakka City, Longboat Key, West Bradenton",
    "Sarasota": "Sarasota, Venice, North Port, Osprey, Nokomis, Englewood, Siesta Key, Laurel, North Venice",
    "Charlotte": "Port Charlotte, Punta Gorda, Rotonda West, Placida, Murdock",
    "Lee": "Fort Myers, Ft Myers, Cape Coral, Bonita Springs, Estero, Lehigh Acres, Fort Myers Beach, Ft Myers Beach, Sanibel, "
           "North Fort Myers, N Fort Myers, Alva, Matlacha, Pine Island, Bokeelia, Saint James City, St James City",
    "Collier": "Naples, Marco Island, Immokalee, Everglades City, Ave Maria, Golden Gate",
    "Hardee": "Wauchula, Bowling Green, Zolfo Springs",
    "Highlands": "Sebring, Avon Park, Lake Placid",
    "DeSoto": "Arcadia",
    "Glades": "Moore Haven",
    "Hendry": "Clewiston, Labelle, La Belle",
    "Sumter": "Bushnell, Wildwood, Webster, Center Hill, Coleman",
    "Levy": "Chiefland, Williston, Cedar Key, Bronson",
    "Alachua": "Gainesville, Hawthorne, Alachua, High Springs, Newberry, Micanopy, Archer",
    "Lake": "Groveland, Clermont, Leesburg, Tavares, Eustis, Mount Dora, Lady Lake, Minneola, Fruitland Park",
    "Indian River": "Vero Beach, Sebastian, Fellsmere",
    "Brevard": "Cocoa, Cocoa Beach, Titusville, Melbourne, Palm Bay, Merritt Island, Rockledge, Port Canaveral, Titusville / Port Canaveral",
    "Volusia": "Daytona Beach, Orange City, Deland, DeLand, Deltona, New Smyrna Beach, Ormond Beach, Port Orange, Cassadaga, Edgewater, Debary",
    "Orange": "Orlando, Winter Park, Apopka, Ocoee, Winter Garden, Maitland, Windermere",
    "Osceola": "Kissimmee, Saint Cloud, St Cloud, Celebration",
    "Seminole": "Sanford, Altamonte Springs, Oviedo, Lake Mary, Longwood, Winter Springs, Casselberry",
    "Marion": "Ocala, Dunnellon, Belleview, Silver Springs",
    "Miami-Dade": "Miami, Miami Beach, Miami Gardens, Hialeah, Homestead, Coral Gables, Doral, Kendall, North Miami, Florida City, Biscayne Bay, Biscayne Bay Miami, Key Biscayne",
    "Broward": "Fort Lauderdale, Ft Lauderdale, Hollywood, Pompano Beach, Coral Springs, Pembroke Pines, Davie, Plantation, Sunrise, Deerfield Beach, Dania Beach, Miramar",
    "Palm Beach": "West Palm Beach, Boca Raton, Delray Beach, Boynton Beach, Jupiter, Lake Worth, Lake Worth Beach, Wellington, Palm Beach Gardens, Belle Glade, Palm Beach",
    "Monroe": "Key West, Key Largo, Islamorada, Marathon, Big Pine Key, Tavernier",
    "Martin": "Stuart, Jensen Beach, Hobe Sound, Palm City",
    "St. Lucie": "Port St Lucie, Port Saint Lucie, Fort Pierce",
    "Okeechobee": "Okeechobee",
    "Duval": "Jacksonville, Jacksonville Beach, Atlantic Beach, Neptune Beach",
    "St. Johns": "St Augustine, Saint Augustine, Ponte Vedra Beach, St Augustine Beach",
    "Flagler": "Palm Coast, Flagler Beach, Bunnell",
    "Leon": "Tallahassee",
    "Escambia": "Pensacola, Perdido Key, Perdido Key (Flora-Bama), Pensacola Beach",
    "Santa Rosa": "Navarre, Milton, Gulf Breeze, Pace",
    "Okaloosa": "Destin, Fort Walton Beach, Niceville, Crestview",
    "Walton": "Santa Rosa Beach, DeFuniak Springs, Miramar Beach, Seaside",
    "Bay": "Panama City, Panama City Beach, Lynn Haven, Mexico Beach",
    "Wakulla": "Sopchoppy, Crawfordville, St Marks",
    "Hardee": "Wauchula, Bowling Green, Zolfo Springs, Ona",
    "Collier": "Naples, Marco Island, Immokalee, Everglades City, Ave Maria, Golden Gate, Ochopee, Everglades",
    "Hendry": "Clewiston, Labelle, La Belle, LaBelle",
    "Polk": "Lakeland, Winter Haven, Bartow, Davenport, Haines City, Auburndale, Lake Wales, Mulberry, Lake Alfred, Poinciana, Frostproof, Fort Meade, Eagle Lake, Dundee, Polk City, Babson Park",
    "Sumter": "Bushnell, Wildwood, Webster, Center Hill, Coleman, The Villages",
    "Columbia": "Lake City", "Clay": "Orange Park, Green Cove Springs, Fleming Island", "Nassau": "Fernandina Beach, Yulee",
    "Putnam": "Palatka", "Citrus": "Crystal River, Inverness, Homosassa, Homosassa Springs, Lecanto, Beverly Hills, Hernando, Floral City",
}
# merge duplicates: later keys override earlier for same county name, so rebuild by appending lists



def _norm(s):
    return " ".join((s or "").lower().replace(".", "").replace("-", " ").split())


CITY_TO_COUNTY = {_norm(c): county for county, cities in _C.items() for c in cities.split(",")}
COUNTY_NAMES = {_norm(k): k for k in _C} | {"dade": "Miami-Dade", "miami dade": "Miami-Dade", "desoto": "DeSoto"}


def county_of_place(text):
    """Best-effort county for free text like 'Palmetto, Manatee County', 'Lakewood Ranch', 'Charlotte County'."""
    import re
    t = text or ""
    m = re.search(r"([A-Za-z.\- ]+?) County", t)
    if m:
        k = _norm(m.group(1).split(",")[-1])
        if k in COUNTY_NAMES:
            return COUNTY_NAMES[k]
    for part in [t] + [x.strip() for x in t.replace("/", ",").replace("(", ",").split(",")]:
        c = CITY_TO_COUNTY.get(_norm(part))
        if c:
            return c
    return None


def county_for(city):
    return CITY_TO_COUNTY.get(_norm(city), "Other")
