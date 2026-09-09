import { ShoppingBag } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useLanguage } from "../context/LanguageContext";
import "../styles/orderHistory.css";

const ORDERS = [
  { id: "ORD-9021", customer: "Ravi Kumar", date: "2026-03-01", items: 3, total: "₹1,450", status: "Completed" },
  { id: "ORD-9022", customer: "Sita Sharma", date: "2026-03-03", items: 1, total: "₹499", status: "Pending" },
  { id: "ORD-9023", customer: "Anand Reddy", date: "2026-03-04", items: 5, total: "₹3,200", status: "Completed" },
  { id: "ORD-9024", customer: "Pooja V.", date: "2026-03-07", items: 2, total: "₹890", status: "Cancelled" },
  { id: "ORD-9025", customer: "Kiran Teja", date: "2026-03-08", items: 4, total: "₹2,150", status: "Completed" },
];

export default function OrderHistory() {
  const navigate = useNavigate();
  const { t } = useLanguage();

  return (
    <div className="orders-page">
      <header className="orders-header">
        <button className="orders-back" onClick={() => navigate("/")}>← Back</button>
        <div className="orders-title"><ShoppingBag size={18} /> {t("Order History")}</div>
      </header>

      <div className="orders-intro">
        <span>{t("ORDERS")}</span>
        <h1>{t("Order History.")}</h1>
        <p>{t("View your recent customer orders and their current status.")}</p>
      </div>

      <div className="orders-table-wrap">
        <table className="orders-table">
          <thead>
            <tr>
              <th>{t("Order ID")}</th>
              <th>{t("Customer")}</th>
              <th>{t("Date")}</th>
              <th>{t("Items")}</th>
              <th>{t("Total")}</th>
              <th>{t("Status")}</th>
            </tr>
          </thead>
          <tbody>
            {ORDERS.map((order) => (
              <tr key={order.id}>
                <td><strong>{order.id}</strong></td>
                <td>{t(order.customer)}</td>
                <td>{order.date}</td>
                <td>{order.items}</td>
                <td>{order.total}</td>
                <td><span className={`order-status ${order.status.toLowerCase()}`}>{t(order.status)}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
