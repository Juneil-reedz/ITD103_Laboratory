// =============================================================
// Lab 4 – Exercise 3: Geospatial Queries
// Requires: address.coord stored as [longitude, latitude] (GeoJSON order)
// Run inside mongosh
// =============================================================

use food

// -------------------------------------------------------------
// 1. Create 2dsphere index for GeoJSON / spherical queries
//    Required for $near, $nearSphere, $geoWithin with GeoJSON
// -------------------------------------------------------------
print("--- Creating 2dsphere index ---")
db.restaurants.createIndex({ "address.coord": "2dsphere" })

// Verify
db.restaurants.getIndexes()

// -------------------------------------------------------------
// 2. $near — find restaurants within 1km of a point
//    Coordinates: [longitude, latitude] in GeoJSON format
//    $maxDistance in meters
//    Results are sorted by distance (closest first) automatically
// -------------------------------------------------------------
print("\n--- 2. Restaurants within 1km of [-73.856077, 40.848447] ---")
db.restaurants.find({
  "address.coord": {
    $near: {
      $geometry: {
        type: "Point",
        coordinates: [-73.856077, 40.848447]
      },
      $maxDistance: 1000   // metres
    }
  }
}, { name: 1, "address.street": 1, _id: 0 })

// Increase radius to 5km
print("\n--- 2b. Restaurants within 5km of Manhattan center ---")
db.restaurants.find({
  "address.coord": {
    $near: {
      $geometry: {
        type: "Point",
        coordinates: [-73.9857, 40.7484]
      },
      $maxDistance: 5000
    }
  }
}, { name: 1, "address.borough": 1, _id: 0 })

// -------------------------------------------------------------
// 3. $geoWithin — find restaurants inside a polygon
//    Polygon must be closed (first = last coordinate)
//    Coordinate order: [longitude, latitude]
// -------------------------------------------------------------
print("\n--- 3. Restaurants within bounding polygon ---")
const polygon = {
  type: "Polygon",
  coordinates: [[
    [-73.9, 40.8],
    [-73.9, 40.9],
    [-73.8, 40.9],
    [-73.8, 40.8],
    [-73.9, 40.8]   // closed — matches first point
  ]]
}

db.restaurants.find({
  "address.coord": {
    $geoWithin: { $geometry: polygon }
  }
}, { name: 1, "address.borough": 1, "address.coord": 1, _id: 0 })

// -------------------------------------------------------------
// 4. $geoWithin with $box — rectangular bounding box
//    Format: [[bottom-left], [top-right]] in [lon, lat]
//    Uses a flat (non-spherical) calculation — good for small areas
// -------------------------------------------------------------
print("\n--- 4. Restaurants in bounding box (Manhattan area) ---")
db.restaurants.find({
  "address.coord": {
    $geoWithin: {
      $box: [
        [-74.02, 40.70],   // bottom-left [lon, lat]
        [-73.93, 40.78]    // top-right [lon, lat]
      ]
    }
  }
}, { name: 1, "address.borough": 1, _id: 0 })

// -------------------------------------------------------------
// 5. $geoWithin with $center — circular area (flat)
//    Format: [[lon, lat], radius_in_radians]
//    1km ≈ 0.00899 radians on Earth's surface
// -------------------------------------------------------------
print("\n--- 5. Restaurants within circular area around Bronx point ---")
db.restaurants.find({
  "address.coord": {
    $geoWithin: {
      $center: [[-73.856077, 40.848447], 0.02]  // ~2.2km radius
    }
  }
}, { name: 1, "address.borough": 1, _id: 0 })
