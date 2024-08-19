import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy import stats

# Set up the page
st.set_page_config(page_title="Advanced Shoup Parking Cost Calculator", layout="wide")
st.title("Advanced Shoup Model for Parking Costs Calculator")

# Add credit
st.sidebar.markdown("""
---
**Developed by:**  
[Dr. Timothy F. Welch](https://profiles.auckland.ac.nz/t-welch)  
University of Auckland
""")

# Tabs for different sections
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["Calculator", "Scenario Comparison", "Advanced Analytics", "Urban Planning", "Workplace Parking", "Methodology", "User Guide"])

with tab1:
    # Sidebar inputs for different scenarios
    st.sidebar.header("Input Parameters")
    scenario_name = st.sidebar.text_input("Scenario Name", "Base Scenario")
    parking_type = st.sidebar.selectbox("Parking Type", ["Surface", "Structured", "Underground"])

    # Advanced inputs with explanations
    with st.sidebar.expander("Advanced Inputs"):
        st.write("Adjust these parameters for more precise calculations.")
        spaces = st.number_input("Number of Parking Spaces", min_value=1.0, value=1.0, step=0.1, help="Total number of parking spaces in the project.")
        years = st.number_input("Years of Use", min_value=1.0, value=1.0, step=0.1, help="Expected lifespan of the parking facility.")
        opportunity_multiplier = st.slider("Opportunity Cost Multiplier", 0.0, 100.0, 50.0, step=0.1, help="Multiplier for the potential alternative use value of the land.")
        
    # Sidebar inputs for costs and rates
    with st.sidebar.expander("Cost Inputs"):
        land_cost = st.number_input("Land Cost per sqm ($)", min_value=0.0, value=1000.0, step=0.1)
        construction_cost = st.number_input("Construction Cost per space ($)", min_value=0.0, value=5000.0, step=0.1)
        maintenance_cost = st.number_input("Maintenance Cost per space per year ($)", min_value=0.0, value=500.0, step=0.1)
        inflation_rate = st.number_input("Inflation Rate (%)", min_value=0.0, value=2.0, step=0.1)
        discount_rate = st.number_input("Discount Rate (%)", min_value=0.0, value=5.0, step=0.1)
        occupancy_rate = st.number_input("Occupancy Rate (%)", min_value=0.0, value=80.0, step=0.1)

    with st.sidebar.expander("Environmental and Other Costs"):
        environmental_cost = st.number_input("Environmental Cost per space per year ($)", min_value=0.0, value=100.0, step=0.1)
        parking_fee = st.number_input("Parking Fee per hour ($)", min_value=0.0, value=2.0, step=0.1)
        car_ownership_rate = st.number_input("Car Ownership Rate (%)", min_value=0.0, value=50.0, step=0.1)
        parking_demand_factor = st.number_input("Parking Demand Factor", min_value=0.0, value=1.0, step=0.1)

    # Perform calculations
    total_land_cost = land_cost * spaces * 15  # Adjusted for 15 sqm per space
    total_construction_cost = construction_cost * spaces

    # Calculate NPV of maintenance costs
    npv_maintenance = 0
    for year in range(1, int(years) + 1):  # Ensure years is converted to int if it's not already
        nominal_maintenance = maintenance_cost * spaces * (1 + inflation_rate/100)**year
        npv_maintenance += nominal_maintenance / (1 + discount_rate/100)**year
    
    total_opportunity_cost = total_land_cost * opportunity_multiplier
    total_environmental_cost = environmental_cost * spaces * years
    
    # Complete the total cost calculation
    total_cost = (total_land_cost + total_construction_cost + 
                  npv_maintenance + total_opportunity_cost + 
                  total_environmental_cost)
    
    cost_per_space = total_cost / spaces
    cost_per_year = total_cost / years

    # Display results with expanded breakdown
    st.header("Results")
    st.subheader(f"Scenario: {scenario_name}")

    # Use columns for a more compact layout
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Total Land Cost:** ${total_land_cost:,.2f}")
        st.write(f"**Total Construction Cost:** ${total_construction_cost:,.2f}")
        st.write(f"**NPV of Maintenance Costs:** ${npv_maintenance:,.2f}")
    with col2:
        st.write(f"**Total Opportunity Cost:** ${total_opportunity_cost:,.2f}")
        st.write(f"**Total Environmental Cost:** ${total_environmental_cost:,.2f}")
        st.write(f"**Total Cost (NPV):** ${total_cost:,.2f}")

    st.write(f"**Cost per Parking Space:** ${cost_per_space:,.2f}")
    st.write(f"**Cost per Year:** ${cost_per_year:,.2f}")

    # Interactive chart for cost breakdown using Plotly
    labels = ['Land Cost', 'Construction Cost', 'Maintenance Cost (NPV)', 'Opportunity Cost', 'Environmental Cost']
    sizes = [total_land_cost, total_construction_cost, npv_maintenance, total_opportunity_cost, total_environmental_cost]
    fig = px.pie(names=labels, values=sizes, title='Cost Breakdown')
    st.plotly_chart(fig)

    # Scenario saving
    if st.button("Save Scenario"):
        if 'scenario_data' not in st.session_state:
            st.session_state['scenario_data'] = []
        
        scenario_data = {
            "Scenario": scenario_name,
            "Type": parking_type,
            "Total Cost (NPV)": total_cost,
            "Cost per Space": cost_per_space,
            "Cost per Year": cost_per_year,
            "Land Cost": total_land_cost,
            "Construction Cost": total_construction_cost,
            "Maintenance Cost (NPV)": npv_maintenance,
            "Opportunity Cost": total_opportunity_cost,
            "Environmental Cost": total_environmental_cost,
            "Inflation Rate": inflation_rate,
            "Discount Rate": discount_rate,
            "Occupancy Rate": occupancy_rate,
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state['scenario_data'].append(scenario_data)
        st.success(f"Scenario '{scenario_name}' saved successfully!")

with tab2:
    # Display saved scenarios with option to remove
    if 'scenario_data' in st.session_state and st.session_state['scenario_data']:
        st.subheader("Scenario Comparison")
        scenario_df = pd.DataFrame(st.session_state['scenario_data'])
        
        # Option to remove scenarios
        scenarios_to_remove = st.multiselect("Select scenarios to remove:", scenario_df['Scenario'].unique())
        if st.button("Remove Selected Scenarios"):
            st.session_state['scenario_data'] = [scenario for scenario in st.session_state['scenario_data'] if scenario['Scenario'] not in scenarios_to_remove]
            scenario_df = pd.DataFrame(st.session_state['scenario_data'])
            st.success("Selected scenarios removed.")
        
        st.dataframe(scenario_df)
        
        # Visualization of multiple scenarios using Plotly
        fig = px.bar(scenario_df, x='Scenario', y=['Land Cost', 'Construction Cost', 'Maintenance Cost (NPV)', 'Opportunity Cost', 'Environmental Cost'])
        st.plotly_chart(fig)  # Ensure this line is complete


        fig = go.Figure()
        for scenario in scenario_df['Scenario']:
            fig.add_trace(go.Scatterpolar(
                r=[scenario_df[scenario_df['Scenario'] == scenario]['Total Cost (NPV)'].values[0],
                   scenario_df[scenario_df['Scenario'] == scenario]['Cost per Space'].values[0],
                   scenario_df[scenario_df['Scenario'] == scenario]['Inflation Rate'].values[0],
                   scenario_df[scenario_df['Scenario'] == scenario]['Discount Rate'].values[0],
                   scenario_df[scenario_df['Scenario'] == scenario]['Occupancy Rate'].values[0]],
                theta=['Total Cost', 'Cost per Space', 'Inflation Rate', 'Discount Rate', 'Occupancy Rate'],
                fill='toself',
                name=scenario
            ))
        fig.update_layout(title="Multi-dimensional Scenario Comparison")
        st.plotly_chart(fig)  # Ensure this line is complete

        # Export data option
        if st.button("Export Data to CSV"):
            csv = scenario_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="parking_cost_scenarios.csv",
                mime="text/csv"
            )  # Closing parenthesis here is important

                
with tab3:
    st.subheader("Advanced Analytics")

    # Sensitivity analysis
    st.write("### Sensitivity Analysis")
    sensitivity_parameter = st.selectbox(
        "Select parameter for sensitivity analysis:",
        ["Land Cost", "Construction Cost", "Maintenance Cost", "Inflation Rate", "Discount Rate", "Occupancy Rate"]
    )

    # Perform sensitivity analysis
    base_value = locals()[sensitivity_parameter.lower().replace(" ", "_")]
    sensitivity_range = [10, 50]  # Example range, replace with your actual range variables
    sensitivity_values = [base_value * (1 + i/100) for i in range(sensitivity_range[0], sensitivity_range[1]+1, 5)]
    sensitivity_results = []

    for value in sensitivity_values:
        locals()[sensitivity_parameter.lower().replace(" ", "_")] = value
        total_cost = (
            land_cost * spaces * 15 +
            construction_cost * spaces +
            maintenance_cost * spaces * years * (1 + inflation_rate/100) / (discount_rate/100) +
            land_cost * spaces * 15 * opportunity_multiplier +
            total_environmental_cost  # Add all expected costs here, replace this with actual variables
        )

        sensitivity_results.append(total_cost)

    fig = px.line(x=sensitivity_values, y=sensitivity_results, labels={'x': sensitivity_parameter, 'y': 'Total Cost'})
    st.plotly_chart(fig)

    # Reset the modified variable
    locals()[sensitivity_parameter.lower().replace(" ", "_")] = base_value

    # Monte Carlo simulation
    st.write("### Monte Carlo Simulation")
    n_simulations = st.slider("Number of Simulations", 0, 100, 50, step=1)  # Ensure integer values

    # Define probability distributions for key parameters
    land_cost_mean, land_cost_std = land_cost, land_cost * 0.1
    construction_cost_mean, construction_cost_std = construction_cost, construction_cost * 0.15
    maintenance_cost_mean, maintenance_cost_std = maintenance_cost, maintenance_cost * 0.2

    # Run Monte Carlo simulation
    simulation_results = []
    for _ in range(int(n_simulations)):
        sim_land_cost = max(0, np.random.normal(land_cost_mean, land_cost_std))
        sim_construction_cost = max(0, np.random.normal(construction_cost_mean, construction_cost_std))
        sim_maintenance_cost = max(0, np.random.normal(maintenance_cost_mean, maintenance_cost_std))

        sim_total_cost = (
            sim_land_cost * spaces * 15 +
            sim_construction_cost * spaces +
            sim_maintenance_cost * spaces * years * (1 + inflation_rate/100) / (discount_rate/100) +
            sim_land_cost * spaces * 15 * opportunity_multiplier +
            total_environmental_cost  # Replace or add other costs here
        )

        simulation_results.append(sim_total_cost)

    # Plot Monte Carlo simulation results
    fig = px.histogram(simulation_results, nbins=50, labels={'value': 'Total Cost', 'count': 'Frequency'})
    st.plotly_chart(fig)

    # Calculate and display statistics
    mean_cost = np.mean(simulation_results)
    median_cost = np.median(simulation_results)
    std_dev = np.std(simulation_results)
    ci_lower, ci_upper = stats.t.interval(0.95, len(simulation_results)-1, loc=mean_cost, scale=stats.sem(simulation_results))

    st.write(f"Mean Total Cost: ${mean_cost:,.2f}")
    st.write(f"Median Total Cost: ${median_cost:,.2f}")
    st.write(f"Standard Deviation: ${std_dev:,.2f}")
    st.write(f"95% Confidence Interval: (${ci_lower:,.2f}, ${ci_upper:,.2f})")


with tab4:
    st.subheader("Urban Planning and Policy Analysis")

    # Street parking analysis
    st.write("### Street Parking Analysis")
    
    street_length = st.number_input("Street Length (meters)", min_value=0.0, value=100.0, step=0.1)
    parking_space_length = st.number_input("Parking Space Length (meters)", min_value=0.0, value=5.0, step=0.1)
    parking_lane_width = st.number_input("Parking Lane Width (meters)", min_value=0.0, value=2.5, step=0.1)
    
    num_street_spaces = int(street_length / parking_space_length)
    street_parking_area = num_street_spaces * parking_space_length * parking_lane_width

    st.write(f"Potential number of street parking spaces: {num_street_spaces}")
    st.write(f"Total area used for street parking: {street_parking_area:.2f} square meters")

    # Alternative use analysis
    st.write("### Alternative Use Analysis")
    alternative_use = st.selectbox("Select alternative use:", ["Bike Lane", "Wider Sidewalk", "Green Space", "Bus Lane"])
    
    if alternative_use == "Bike Lane":
        bike_lane_width = 1.5
        bike_lane_length = street_length
        st.write(f"Potential bike lane length: {bike_lane_length} meters")
        st.write(f"Bike lane area: {bike_lane_length * bike_lane_width:.2f} square meters")
    elif alternative_use == "Wider Sidewalk":
        sidewalk_width_increase = parking_lane_width
        st.write(f"Potential sidewalk width increase: {sidewalk_width_increase} meters")
        st.write(f"Additional sidewalk area: {street_length * sidewalk_width_increase:.2f} square meters")
    elif alternative_use == "Green Space":
        green_space_area = street_parking_area
        st.write(f"Potential green space area: {green_space_area:.2f} square meters")
    elif alternative_use == "Bus Lane":
        bus_lane_length = street_length
        st.write(f"Potential bus lane length: {bus_lane_length} meters")

    # Parking demand estimation
    st.write("### Parking Demand Estimation")
    population = st.number_input("Local Population", min_value=0.0, value=0.0, step=0.1)

    estimated_parking_demand = int(population * car_ownership_rate * parking_demand_factor)
    st.write(f"Estimated parking demand: {estimated_parking_demand} spaces")

    # Parking policy impact
    st.write("### Parking Policy Impact")
    price_elasticity = st.slider("Price Elasticity of Demand", 0.0, 100.0, 50.0, step=0.1, help="Typically between -0.1 to -0.6 for parking")
    
    demand_change = price_elasticity * (parking_fee / 2 - 1)  # Assuming a base price of $2/hour
    new_demand = int(estimated_parking_demand * (1 + demand_change))
    
    st.write(f"Estimated change in parking demand: {demand_change:.2%}")
    st.write(f"New estimated parking demand: {new_demand} spaces")

    # Visualization of policy impact
    fig = go.Figure()
    fig.add_trace(go.Bar(x=['Current Demand', 'New Demand'], y=[estimated_parking_demand, new_demand]))
    fig.update_layout(title="Impact of Parking Fee on Demand")
    st.plotly_chart(fig)

with tab5:
    st.subheader("Workplace Parking Cost Analysis")
    
    st.write("""
    This section helps businesses and organizations calculate the true cost of providing parking for employees. 
    It considers both direct costs and opportunity costs associated with workplace parking.
    """)

    # Input parameters
    num_spaces = st.number_input("Number of Parking Spaces", min_value=1, value=100, step=1)
    parking_type = st.selectbox("Parking Type", ["Surface Lot", "Structured Parking", "Underground"])
    location = st.selectbox("Location Type", ["Urban Center", "Suburban", "Rural"])

    # Costs based on parking type and location (these are example values and should be adjusted based on real data)
    cost_per_space = {
        "Surface Lot": {"Urban Center": 5000, "Suburban": 3000, "Rural": 2000},
        "Structured Parking": {"Urban Center": 20000, "Suburban": 15000, "Rural": 12000},
        "Underground": {"Urban Center": 35000, "Suburban": 25000, "Rural": 20000}
    }

    land_cost_per_sqm = {"Urban Center": 1000, "Suburban": 500, "Rural": 200}
    
    # Calculate costs
    construction_cost = num_spaces * cost_per_space[parking_type][location]
    land_area = num_spaces * (30 if parking_type == "Surface Lot" else 15)  # 30 sqm for surface, 15 for others
    land_cost = land_area * land_cost_per_sqm[location]
    
    annual_maintenance = num_spaces * 500  # Assume $500 per space per year for maintenance
    
    # Opportunity cost (assuming the space could be rented out if not used for parking)
    monthly_rent_per_sqm = {"Urban Center": 50, "Suburban": 30, "Rural": 15}
    annual_opportunity_cost = land_area * monthly_rent_per_sqm[location] * 12

    # Total annual cost
    total_annual_cost = (construction_cost + land_cost) * 0.05 + annual_maintenance + annual_opportunity_cost

    # Display results
    st.write(f"Construction Cost: ${construction_cost:,.2f}")
    st.write(f"Land Cost: ${land_cost:,.2f}")
    st.write(f"Annual Maintenance Cost: ${annual_maintenance:,.2f}")
    st.write(f"Annual Opportunity Cost: ${annual_opportunity_cost:,.2f}")
    st.write(f"Total Annual Cost: ${total_annual_cost:,.2f}")
    st.write(f"Cost per Space per Year: ${total_annual_cost/num_spaces:,.2f}")
    st.write(f"Cost per Space per Month: ${total_annual_cost/num_spaces/12:,.2f}")
    
    fig = go.Figure(data=[
        go.Bar(name='Construction', y=['Cost'], x=[construction_cost], orientation='h'),
        go.Bar(name='Land', y=['Cost'], x=[land_cost], orientation='h'),
        go.Bar(name='Annual Maintenance', y=['Cost'], x=[annual_maintenance], orientation='h'),
        go.Bar(name='Annual Opportunity Cost', y=['Cost'], x=[annual_opportunity_cost], orientation='h')
    ])
    fig.update_layout(barmode='stack', title='Breakdown of Parking Costs')
    st.plotly_chart(fig)

    # Alternative analysis
    st.subheader("Alternative Analysis")
    st.write("Consider alternatives to providing parking:")

    # Public transit subsidy
    monthly_transit_pass = st.number_input("Monthly Transit Pass Cost ($)", min_value=0, value=100, step=10)
    annual_transit_subsidy = monthly_transit_pass * 12 * num_spaces
    st.write(f"Annual cost to subsidize public transit instead: ${annual_transit_subsidy:,.2f}")

    # Remote work
    days_remote = st.slider("Number of Remote Work Days per Week", 0, 5, 2, step=1)
    reduced_parking_need = num_spaces * (1 - days_remote/5)
    reduced_annual_cost = total_annual_cost * (1 - days_remote/5)
    st.write(f"Reduced parking need with {days_remote} remote days: {reduced_parking_need:.0f} spaces")
    st.write(f"Reduced annual cost: ${reduced_annual_cost:,.2f}")

    # Carpooling incentive
    carpool_rate = st.slider("Percentage of Employees Carpooling", 0, 100, 20, step=5)
    carpool_incentive = st.number_input("Monthly Carpool Incentive per Employee ($)", min_value=0, value=50, step=10)
    carpool_spaces_saved = num_spaces * carpool_rate/100 * 0.5  # Assume each carpool saves 0.5 spaces
    carpool_annual_cost = carpool_incentive * 12 * (num_spaces * carpool_rate/100)
    carpool_annual_savings = total_annual_cost * (carpool_spaces_saved / num_spaces) - carpool_annual_cost
    st.write(f"Spaces saved through carpooling: {carpool_spaces_saved:.0f}")
    st.write(f"Annual cost of carpooling incentives: ${carpool_annual_cost:,.2f}")
    st.write(f"Potential annual savings: ${carpool_annual_savings:,.2f}")

    # Comparison chart
    fig = go.Figure(data=[
        go.Bar(name='Current Parking Cost', x=['Cost'], y=[total_annual_cost]),
        go.Bar(name='Public Transit Subsidy', x=['Cost'], y=[annual_transit_subsidy]),
        go.Bar(name='Remote Work (Reduced Parking)', x=['Cost'], y=[reduced_annual_cost]),
        go.Bar(name='Carpooling Incentive', x=['Cost'], y=[total_annual_cost - carpool_annual_savings])
    ])
    fig.update_layout(title='Comparison of Parking Alternatives')
    st.plotly_chart(fig)

with tab6:
    st.subheader("Methodology & Assumptions")
    st.write("""
    This calculator uses an advanced version of the Shoup model for estimating parking costs. Key features and assumptions include:

    1. **Land Use**: We assume 15 square meters per parking space, which includes the space itself and necessary access lanes.
    
    2. **Net Present Value (NPV)**: All future costs are discounted to present value using the specified discount rate, allowing for more accurate long-term cost estimates.
    
    3. **Inflation**: The model accounts for inflation in maintenance costs over time.
    
    4. **Opportunity Cost**: This represents the potential value of the land if used for purposes other than parking.
    
    5. **Environmental Cost**: An estimate of the environmental impact of creating and maintaining parking spaces.
    
    6. **Sensitivity Analysis**: This feature allows users to understand how changes in key parameters affect the total cost.
    
    7. **Monte Carlo Simulation**: This advanced feature accounts for uncertainty in cost estimates by running multiple simulations with randomly varied inputs.

    The model aims to provide a comprehensive view of parking costs, including often-overlooked factors like opportunity costs and environmental impacts. However, users should note that local conditions and specific project details may necessitate adjustments to these calculations.

    **Additional Methodologies for Urban Planning:**

    1. **Street Parking Analysis**: Estimates the number of potential parking spaces and area used based on street dimensions.
    
    2. **Alternative Use Analysis**: Provides insights into potential alternative uses for street parking spaces.
    
    3. **Parking Demand Estimation**: Uses population, car ownership rates, and local factors to estimate parking demand.
    
    4. **Parking Policy Impact**: Utilizes price elasticity of demand to estimate the impact of parking fees on demand.

    These additional features aim to provide urban planners and policymakers with tools to assess the broader impacts of parking policies and alternative land uses. The calculations are simplified models and should be adjusted based on specific local conditions and more detailed data when available.

    For more detailed information on parking economics, refer to:
    - "The High Cost of Free Parking" by Donald Shoup
    - "Parking and the City" edited by Donald Shoup
    - Victoria Transport Policy Institute's "Transportation Cost and Benefit Analysis II – Parking Costs"
    """)

with tab7:
    st.subheader("User Guide")
    st.write("""
    Welcome to the Advanced Shoup Parking Cost Calculator! This guide will help you navigate the various features of this tool.

    ### 1. Calculator Tab
    - Input your scenario parameters in the sidebar.
    - View the cost breakdown and results.
    - Save scenarios for later comparison.

    ### 2. Scenario Comparison Tab
    - Compare multiple saved scenarios.
    - Visualize differences using bar charts and radar plots.
    - Export scenario data to CSV for further analysis.

    ### 3. Advanced Analytics Tab
    - Perform sensitivity analysis on key parameters.
    - Run Monte Carlo simulations to account for uncertainty.
    - View statistical summaries of simulation results.

    ### 4. Urban Planning Tab
    - Analyze street parking potential and alternative uses.
    - Estimate parking demand based on population and local factors.
    - Assess the impact of parking policies on demand.

    ### 5. Workplace Parking Tab
    - Calculate the true cost of providing employee parking.
    - Consider construction, land, maintenance, and opportunity costs.
    - Explore alternatives like public transit subsidies, remote work, and carpooling incentives.
    - Compare costs of different parking strategies for your organization.

    ### 6. Methodology Tab
    - Understand the underlying assumptions and calculations.
    - Learn about the Shoup model and its extensions.

    ### Tips for Use:
    - Start with the Calculator tab to input your base scenario.
    - Use the Scenario Comparison to evaluate different options.
    - Leverage Advanced Analytics for more in-depth understanding.
    - Utilize the Urban Planning features for broader policy considerations.
    - Use the Workplace Parking tab for business-specific parking cost analysis.
    - Refer to the Methodology tab to understand the underlying principles.

    Remember, while this tool provides valuable insights, it should be used in conjunction with local knowledge and additional data for making real-world decisions.
    """)


# Footer with additional resources
st.markdown("---")
st.markdown("""
**Additional Resources:**
- [The High Cost of Free Parking by Donald Shoup](https://www.routledge.com/The-High-Cost-of-Free-Parking-Updated-Edition/Shoup/p/book/9781932364965)
- [Parking and the City](https://www.routledge.com/Parking-and-the-City/Shoup/p/book/9781138497122)
- [Victoria Transport Policy Institute - Parking Costs](https://www.vtpi.org/tca/tca0504.pdf)
- [Urban Planning and Transportation Research Resources](https://www.planetizen.com/tag/parking)
- [Workplace Parking Levies: A Review of Evidence](https://www.tandfonline.com/doi/full/10.1080/01441647.2016.1177722)
    """)