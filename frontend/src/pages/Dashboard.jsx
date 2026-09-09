// import { useNavigate } from "react-router-dom";
// import {
//   LayoutDashboard,
//   Plus,
//   Package,
//   FileText,
//   ShoppingBag,
//   BarChart3,
//   Settings,
//   Bell,
//   Search,
//   ArrowUpRight,
//   MoreHorizontal,
//   Mic,
//   Sparkles,
//   IndianRupee,
// } from "lucide-react";

// import "../styles/dashboard.css";

// function Dashboard() {
//   const navigate = useNavigate();
//   const products = [
//     {
//       name: "Handwoven Cotton Saree",
//       category: "Handloom",
//       price: "₹2,599",
//       status: "Published",
//       image:
//         "https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=500&q=80",
//     },
//     {
//       name: "Bamboo Handcrafted Basket",
//       category: "Handicraft",
//       price: "₹850",
//       status: "Draft",
//       image:
//         "https://images.unsplash.com/photo-1584302179602-e4c3d3fd629d?auto=format&fit=crop&w=500&q=80",
//     },
//     {
//       name: "Traditional Terracotta Pot",
//       category: "Pottery",
//       price: "₹1,200",
//       status: "Published",
//       image:
//         "https://images.unsplash.com/photo-1610701596007-11502861dcfa?auto=format&fit=crop&w=500&q=80",
//     },
//   ];

//   return (
//     <div className="dashboard">

//       {/* SIDEBAR */}
//       <aside className="sidebar">

//         <div className="brand">
//           <div className="brand-mark">✦</div>
//           <div>
//             <h2>CraftMitra</h2>
//             <span>Virtual Artisan Manager</span>
//           </div>
//         </div>

//         <nav className="sidebar-nav">

//           <p className="nav-label">MENU</p>

//           <a className="nav-item active">
//             <LayoutDashboard size={19} />
//             <span>Dashboard</span>
//           </a>

//           <button
//             className="nav-item"
//             onClick={() => navigate("/add-product")}
//             >
//             <Plus size={19} />
//             <span>Add Product</span>
//         </button>

//           <button
//             className="nav-item"
//             onClick={() => navigate("/my-products")}
//             >
//             <Package size={19} />
//             <span>My Products</span>
//             </button>

//           <a className="nav-item">
//             <FileText size={19} />
//             <span>Drafts</span>
//             <span className="nav-count">4</span>
//           </a>

//           <a className="nav-item">
//             <ShoppingBag size={19} />
//             <span>Orders</span>
//           </a>

//           <a className="nav-item">
//             <BarChart3 size={19} />
//             <span>Analytics</span>
//           </a>

//           <p className="nav-label second-label">ACCOUNT</p>

//           <a className="nav-item">
//             <Settings size={19} />
//             <span>Settings</span>
//           </a>

//         </nav>

//         {/* AI ASSISTANT */}
//         {/* <div className="assistant-card">
//           <div className="assistant-icon">
//             <Sparkles size={18} />
//           </div>

//           <div className="assistant-content">
//             <strong>Need help?</strong>
//             <span>Ask your AI assistant</span>
//           </div>

//           <Mic size={18} />
//         </div> */}

//       </aside>


//       {/* MAIN CONTENT */}
//       <main className="main-content">

//         {/* TOP BAR */}
//         <header className="topbar">

//           <div className="search-box">
//             <Search size={18} />
//             <input
//               type="text"
//               placeholder="Search products, orders..."
//             />
//           </div>

//           <div className="topbar-right">

//             <button className="notification">
//               <Bell size={19} />
//               <span></span>
//             </button>

//             <div className="profile">

//               <div className="profile-avatar">
//                 M
//               </div>

//               <div className="profile-info">
//                 <strong>Manu</strong>
//                 <span>Artisan</span>
//               </div>

//               <span className="profile-arrow">⌄</span>

//             </div>

//           </div>

//         </header>


//         {/* PAGE HEADER */}
//         <section className="page-header">

//           <div>
//             <p className="eyebrow">
//               YOUR BUSINESS OVERVIEW
//             </p>

//             <h1>
//               Good morning, Manu <span>👋</span>
//             </h1>

//             <p className="subtitle">
//               Here's how your craft business is doing today.
//             </p>
//           </div>

//         <button
//             className="add-product-btn"
//             onClick={() => navigate("/add-product")}
//         >
//             <Plus size={19} />
//             Add Product
//         </button>

//         </section>


//         {/* STAT CARDS */}
//         <section className="stats-grid">

//           <div className="stat-card">

//             <div className="stat-top">
//               <div className="stat-icon green">
//                 <Package size={20} />
//               </div>

//               <span className="stat-growth">
//                 +3 this month
//               </span>
//             </div>

//             <p>Total Products</p>

//             <h2>12</h2>

//             <span className="stat-description">
//               8 published · 4 drafts
//             </span>

//           </div>


//           <div className="stat-card">

//             <div className="stat-top">
//               <div className="stat-icon orange">
//                 <ShoppingBag size={20} />
//               </div>

//               <span className="stat-growth">
//                 +12%
//               </span>
//             </div>

//             <p>Orders</p>

//             <h2>4</h2>

//             <span className="stat-description">
//               2 pending · 2 completed
//             </span>

//           </div>


//           <div className="stat-card">

//             <div className="stat-top">
//               <div className="stat-icon gold">
//                 <IndianRupee size={20} />
//               </div>

//               <span className="stat-growth">
//                 +18%
//               </span>
//             </div>

//             <p>Total Earnings</p>

//             <h2>₹18,450</h2>

//             <span className="stat-description">
//               Compared to last month
//             </span>

//           </div>


//           <div className="stat-card">

//             <div className="stat-top">
//               <div className="stat-icon brown">
//                 <BarChart3 size={20} />
//               </div>

//               <span className="stat-growth">
//                 +24%
//               </span>
//             </div>

//             <p>Product Views</p>

//             <h2>324</h2>

//             <span className="stat-description">
//               82 views this week
//             </span>

//           </div>

//         </section>


//         {/* LOWER CONTENT */}
//         <section className="dashboard-grid">

//           {/* PRODUCTS */}
//           <div className="products-section">

//             <div className="section-header">

//               <div>
//                 <h2>Your Products</h2>
//                 <p>Manage your latest craft listings</p>
//               </div>

//              <button
//                 className="view-all"
//                 onClick={() => navigate("/my-products")}
//                 >
//                 View all
//                 <ArrowUpRight size={16} />
//                 </button>

//             </div>


//             <div className="products-grid">

//               {products.map((product, index) => (

//                 <div className="product-card" key={index}>

//                   <div className="product-image-wrapper">

//                     <img
//                       src={product.image}
//                       alt={product.name}
//                     />

//                     <button className="product-more">
//                       <MoreHorizontal size={18} />
//                     </button>

//                   </div>

//                   <div className="product-info">

//                     <span className="product-category">
//                       {product.category}
//                     </span>

//                     <h3>{product.name}</h3>

//                     <div className="product-bottom">

//                       <strong>{product.price}</strong>

//                       <span
//                         className={`status ${
//                           product.status === "Published"
//                             ? "published"
//                             : "draft"
//                         }`}
//                       >
//                         <span></span>
//                         {product.status}
//                       </span>

//                     </div>

//                   </div>

//                 </div>

//               ))}

//             </div>

//           </div>


//           {/* AI CARD */}
//           <div className="ai-card">

//             <div className="ai-decoration"></div>

//             <div className="ai-content">

//               <div className="ai-icon">
//                 <Sparkles size={22} />
//               </div>

//               <p className="ai-label">
//                 CRAFTMITRA AI
//               </p>

//               <h2>
//                 Your craft has a story.
//                 <br />
//                 Let AI tell it.
//               </h2>

//               <p>
//                 Create professional product listings,
//                 understand your market and reach more
//                 buyers — simply using your voice.
//               </p>

//               <button className="ai-button">
//                 <Mic size={18} />
//                 Talk to your assistant
//               </button>

//             </div>

//           </div>

//         </section>

//       </main>

//     </div>
//   );
// }

// export default Dashboard;

import { useNavigate } from "react-router-dom";
import {
  Plus,
  Package,
  ShoppingBag,
  Bell,
  Search,
  Sparkles,
  Mic,
} from "lucide-react";

import "../styles/dashboard.css";

function Dashboard() {
  const navigate = useNavigate();

  return (
    <div className="dashboard">
      {/* MAIN CONTENT */}
      <main className="main-content">

        {/* TOP BAR */}
        <header className="topbar">

          <div className="search-box">
            <Search size={18} />

            <input
              type="text"
              placeholder="Search products, orders..."
            />
          </div>

          <div className="topbar-right">

            <button className="notification">
              <Bell size={19} />
              <span></span>
            </button>

            <div className="profile">

              <div className="profile-avatar">
                M
              </div>

              <div className="profile-info">
                <strong>Manu</strong>
                <span>Artisan</span>
              </div>

              <span className="profile-arrow">⌄</span>

            </div>

          </div>

        </header>


        {/* AI CARD */}
        <section className="ai-card">

          <div className="ai-decoration"></div>

          <div className="ai-content">

            <div className="ai-icon">
              <Sparkles size={22} />
            </div>

            <p className="ai-label">
              CRAFTMITRA AI
            </p>

            <h2>
              Your craft has a story.
              <br />
              Let AI tell it.
            </h2>

            <p>
              Create professional product listings,
              understand your market and reach more
              buyers — simply using your voice.
            </p>

            <button
              className="ai-button"
              onClick={() => navigate("/add-product")}
            >
              <Mic size={18} />
              Add Your Product
            </button>

          </div>

        </section>

      </main>

    </div>
  );
}

export default Dashboard;