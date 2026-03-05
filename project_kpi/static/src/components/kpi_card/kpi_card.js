/** @odoo-module **/
import { Component } from "@odoo/owl";

export class KpiCard extends Component {
    static template = "project_kpi.KpiCard";
    static props = {
        title: String,
        value: { type: [Number, String] },
        icon: { type: String, optional: true },
        color: { type: String, optional: true },
    };
    static defaultProps = { icon: "fa-chart-bar", color: "primary" };
}