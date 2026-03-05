/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { KpiCard } from "../kpi_card/kpi_card";
import { KpiChart } from "../kpi_chart/kpi_chart";

export class KpiDashboard extends Component {
    static template = "project_kpi.DashboardMain";
    static components = { KpiCard, KpiChart }; 

    setup() {
        this.orm = useService("orm");
        
        this.state = useState({
            filters: {
                year: new Date().getFullYear().toString(),
                month: '',
                department_id: '', 
            },
            data: { 
                summary: {}, 
                charts: { labels: [], datasets: [] }, 
                status_data: { labels: [], datasets: [] }, 
                top_users: [],
                filters: { years: [], departments: [] }, 
            },
            isLoading: true,
        });

        onWillStart(async () => {
            await this.fetchData();
        });
    }

    async fetchData() {
        this.state.isLoading = true;
        try {
            const result = await this.orm.call("kpi.dashboard", "get_dashboard_data", [this.state.filters]);
            this.state.data = {
                summary: result.summary || {},
                charts: result.charts || { labels: [], datasets: [] },
                status_data: result.status_data || { labels: [], datasets: [] }, 
                top_users: result.top_users || [],
                filters: result.filters || { years: [], departments: [] }
            };
        } finally {
            this.state.isLoading = false;
        }
    }

    async updateFilter(field, event) {
        this.state.filters[field] = event.target.value;
        await this.fetchData(); 
    }
}

registry.category("actions").add("project_kpi_dashboard", KpiDashboard);