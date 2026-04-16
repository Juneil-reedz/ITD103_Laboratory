// =============================================================
// Lab 2 – Part B: Document Database Design & Implementation
// Run inside mongosh
// =============================================================

// -------------------------------------------------------------
// Switch to ecommerce database
// -------------------------------------------------------------
use ecommerce

// =============================================================
// PART 1: PRODUCTS COLLECTION
// Schema: embedded variants + embedded reviews (denormalized)
// Rationale: variants and reviews are always read with the product
// =============================================================

db.products.insertMany([
  {
    _id: 1,
    name: "Laptop",
    price: 999.99,
    category: "Electronics",
    variants: [
      { color: "Silver", stock: 50 },
      { color: "Black",  stock: 30 }
    ],
    reviews: [
      { user: "Alice", rating: 5, comment: "Excellent!" },
      { user: "Bob",   rating: 4, comment: "Good value" }
    ]
  },
  {
    _id: 2,
    name: "Wireless Mouse",
    price: 29.99,
    category: "Electronics",
    variants: [
      { color: "White", stock: 100 },
      { color: "Black", stock: 80  }
    ],
    reviews: [
      { user: "Charlie", rating: 3, comment: "Average build quality" },
      { user: "Diana",   rating: 5, comment: "Works perfectly!" }
    ]
  },
  {
    _id: 3,
    name: "Running Shoes",
    price: 79.99,
    category: "Sports",
    variants: [
      { color: "Red",  stock: 20 },
      { color: "Blue", stock: 15 }
    ],
    reviews: [
      { user: "Eve",  rating: 5, comment: "Very comfortable" },
      { user: "Frank", rating: 4, comment: "Great for long runs" }
    ]
  }
])

// =============================================================
// PART 2: ORDERS COLLECTION
// Schema: embedded customer snapshot + referenced product_id
// Rationale: customer info is snapshotted at order time;
//            product_id is referenced for catalog lookups
// =============================================================

db.orders.insertMany([
  {
    order_id: "ORD001",
    customer: { name: "Alice", email: "alice@email.com" },
    items: [
      { product_id: 1, quantity: 1, variant: "Silver" }
    ],
    total: 999.99,
    status: "pending",
    created_at: new Date()
  },
  {
    order_id: "ORD002",
    customer: { name: "Bob", email: "bob@email.com" },
    items: [
      { product_id: 2, quantity: 2, variant: "Black" },
      { product_id: 3, quantity: 1, variant: "Red"   }
    ],
    total: 139.97,
    status: "shipped",
    created_at: new Date()
  }
])

// =============================================================
// PART 3: BLOG SYSTEM COLLECTION
// Schema: embedded author + embedded comments (with replies)
// =============================================================

db.blog_posts.insertMany([
  {
    title: "Getting Started with NoSQL",
    slug: "getting-started-nosql",
    author: { name: "Alice", email: "alice@blog.com" },
    content: "NoSQL databases provide flexible schemas...",
    tags: ["nosql", "mongodb", "database"],
    published_at: new Date("2024-01-15"),
    comments: [
      {
        comment_id: 1,
        user: "Bob",
        text: "Great intro!",
        posted_at: new Date("2024-01-16"),
        replies: [
          {
            user: "Alice",
            text: "Thanks Bob!",
            posted_at: new Date("2024-01-16")
          }
        ]
      },
      {
        comment_id: 2,
        user: "Charlie",
        text: "Very helpful article.",
        posted_at: new Date("2024-01-17"),
        replies: []
      }
    ]
  }
])

// =============================================================
// PART 4: QUERIES
// =============================================================

// 1. Find products with any review rating > 4
db.products.find({ "reviews.rating": { $gt: 4 } })

// 2. Decrement Silver variant stock by 1 when an order is placed
db.products.updateOne(
  { _id: 1, "variants.color": "Silver" },
  { $inc: { "variants.$.stock": -1 } }
)

// Verify stock update
db.products.findOne({ _id: 1 }, { variants: 1 })

// 3. Aggregate: Average rating per product
db.products.aggregate([
  { $unwind: "$reviews" },
  {
    $group: {
      _id: "$name",
      avgRating: { $avg: "$reviews.rating" },
      totalReviews: { $sum: 1 }
    }
  },
  { $sort: { avgRating: -1 } }
])

// 4. Find all orders with status "pending"
db.orders.find({ status: "pending" })

// 5. Find orders containing a specific product
db.orders.find({ "items.product_id": 1 })

// 6. Update order status
db.orders.updateOne(
  { order_id: "ORD001" },
  { $set: { status: "shipped" } }
)

// 7. Products by category with count
db.products.aggregate([
  { $group: { _id: "$category", count: { $sum: 1 } } }
])

// 8. Find blog posts by tag
db.blog_posts.find({ tags: "nosql" })

// 9. Find blog posts that have replies in any comment
db.blog_posts.find({ "comments.replies.0": { $exists: true } })
