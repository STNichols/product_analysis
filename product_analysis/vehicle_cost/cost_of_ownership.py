# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 18:29:56 2020

@author: Sean
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go

class vehicle():
    """ This is a vehicle that will assist in the calculation of cost of
    ownership over the lifetime of the vehicle
    """
    
    def __init__(self, price_tag, payment_duration=None):
        """ Setup default parameters for the vehicle"""
        
        self.mileage = 200000
        self.miles_per_year = 20000
        self.vehicle_price = price_tag
        self.payment_duration = payment_duration
        
        # Prices per miles
        self.vehicle_ppm = self.vehicle_price / self.mileage 
        self.energy_ppm = None
        self.maintenance_ppm = 0
        self.moving_ppm = 0
        
    def add_mileage(self, miles):
        """ Increase the total mileage driven on the car"""
        
        previous_miles = self.mileage
        self.mileage += miles
        
        # Update ppm
        self.vehicle_ppm *= (previous_miles / self.mileage)
        
    def add_maintenance_cost(self, price, miles_per_service):
        """ Accounting for routine maintenance at a predictable interval"""
        
        # Calculate the price per mile (ppm) associated
        ppm = price / miles_per_service
        self.maintenance_ppm += ppm
        self.moving_ppm += ppm
        
    def add_energy_cost(self):
        """ Add the energy price per mile to the overall moving price per mile
        """
        
        if self.energy_ppm is not None:
            self.moving_ppm = self.maintenance_ppm + self.energy_ppm
        
    def cost_at_year(self, year=None):
        """ Calculating the cost of ownership of the vehicle
        
        Args:
            year (int/float/numpy.array): Year value to calculate the cost at
            
        Returns:
            (numpy.array): Total cost of ownership over years
        """
        
        if year is None:
            return np.array([self.vehicle_price +
                             (self.moving_ppm * self.mileage)])
        else:
            if isinstance(year, int) or isinstance(year, float):
                year = np.array([year])
            mpy = self.miles_per_year * year
            if self.payment_duration is None:
                return np.array([(self.vehicle_ppm + self.moving_ppm) * mpy])
            else:
                percent_paid = year / self.payment_duration
                percent_paid = np.min(np.vstack(
                    [percent_paid, np.ones(len(percent_paid))]), axis=0)
                return np.array([((self.vehicle_price * percent_paid) +
                        (self.moving_ppm * mpy))])
            
    def cost_of_ownership(self, years):
        """ Calculating the cost of ownership over the years """
        
        years = np.arange(years * 12 + 1) / 12

        for year in years:
            if year == years[0]:
                coo_stack = self.cost_at_year(year)
                continue
            coo_stack = np.vstack((coo_stack, self.cost_at_year(year)))

        df = pd.DataFrame(data=np.vstack((years, coo_stack.mean(axis=1))).T,
            columns=['year', 'cost_mean'])
        
        # Aggregate the cost variation into columns
        if coo_stack.shape[1] > 1:
            df['cost_min'] = coo_stack.min(axis=1)
            df['cost_max'] = coo_stack.max(axis=1)
        return df

    def plot_cost_of_ownership(self, years, fig=None):
        """ Plot cost of ownership up to the years provided """

        if fig is None:
            fig = go.Figure()

        coo = self.cost_of_ownership(years)

        fig.add_trace(go.Scatter(x=coo['year'], y=coo['cost_mean'],
            mode='lines+markers', name='Mean Cost',
            line_color=self.colors[0]))

        if ('cost_min' in coo) and ('cost_max' in coo):
            fig.add_trace(go.Scatter(x=coo['year'], y=coo['cost_min'],
                    fill=None, mode='lines', line_color=self.colors[1]))
            fig.add_trace(go.Scatter(x=coo['year'], y=coo['cost_max'],
                    fill='tonexty', mode='lines', line_color=self.colors[1]))

        return fig
        
class ice_vehicle(vehicle):
    """ This is an internal combustion vehicle with assistance in calculating
    the cost of ownership parameters
    """
    
    def __init__(self, price_tag, mpg, payment_duration=None, name=None):
        super(ice_vehicle, self).__init__(price_tag,
                                          payment_duration=payment_duration)
        if name is None:
            self.name = 'ICE Vehicle'
        else:
            self.name = name
        
        # Add in oil changes, $40 per 5,000 miles
        self.add_maintenance_cost(40, 5000)
        
        # Add the energy cost into the moving price per miles
        self.miles_per_gallon = mpg
        self.update_energy_ppm(2.50)

        # Color set
        self.colors = ['darkred', 'red', 'lightsalmon', 'orangered']

    def update_energy_ppm(self, gas_cost):
        """ Updating the energy price for a gas vehicle per mile """

        if isinstance(gas_cost, int) or isinstance(gas_cost, float):
            gas_cost = np.array([gas_cost])
        self.gas_price_per_gallon = gas_cost
        self.energy_ppm = self.gas_price_per_gallon / self.miles_per_gallon

        self.add_energy_cost()
        
class electric_vehicle(vehicle):
    """ This is an electric vehicle with assistance in calculating the
    cost of ownership parameters
    """
    
    def __init__(self, price_tag, battery_size_kwh, range_mi,
                 payment_duration=None, name=None):
        super(electric_vehicle, self).__init__(price_tag,
                                         payment_duration=payment_duration)
        if name is None:
            self.name = 'Electric Vehicle'
        else:
            self.name = name
        self.range = range_mi
        self.battery_size = battery_size_kwh
        self.update_energy_ppm(0.13) # Default to $0.13 per kwh

        # Color set
        self.colors = ['darkseagreen', 'green', 'limegreen', 'lightseagreen']
        
    def update_energy_ppm(self, electricity_cost):
        """ Updating the energy price of traveling per mile """
        
        if (isinstance(electricity_cost, int) or
            isinstance(electricity_cost, float)):
            electricity_cost = np.array([electricity_cost])
        self.price_per_kwh = electricity_cost
        self.miles_per_kwh = self.range / self.battery_size
        self.energy_ppm = self.price_per_kwh / self.miles_per_kwh
        
        self.add_energy_cost() 
