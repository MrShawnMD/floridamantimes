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
}


def _norm(s):
    return " ".join((s or "").lower().replace(".", "").replace("-", " ").split())


CITY_TO_COUNTY = {_norm(c): county for county, cities in _C.items() for c in cities.split(",")}


def county_for(city):
    return CITY_TO_COUNTY.get(_norm(city), "Other")
