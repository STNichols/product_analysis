# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 18:29:56 2020

@author: Sean
"""

import numpy as np
import matplotlib.pyplot as plt

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
        
    def cost_of_ownership(self, years=None):
        """ Calculating the cost of ownership of the vehicle
        
        Args:
            years (int/float/numpy.array): Year value to calculate the cost at
            
        Returns:
            (numpy.array): Total cost of ownership over years
        """
        
        if years is None:
            return np.array([self.vehicle_price +
                             (self.moving_ppm * self.mileage)])
        else:
            if isinstance(years, int) or isinstance(years, float):
                years = np.array([years])
            mpy = self.miles_per_year * years
            if self.payment_duration is None:
                return (self.vehicle_ppm + self.moving_ppm) * mpy
            else:
                percent_paid = years / self.payment_duration
                percent_paid = np.min(np.vstack(
                    [percent_paid,np.ones(len(percent_paid))]), axis=0)
                return ((self.vehicle_price * percent_paid) +
                        (self.moving_ppm * mpy))
            
    def plot_cost_of_ownership(self, years, ax=None):
        """ Plot the total cost of ownership over the years"""
        
        if ax is None:
            fig, ax = plt.subplots()
        ax.plot(years, self.cost_of_ownership(years), '.-', label=self.type)
        
class ice_vehicle(vehicle):
    """ This is an internal combustion vehicle with assistance in calculating
    the cost of ownership parameters
    """
    
    def __init__(self, price_tag, mpg, payment_duration=None):
        super(ice_vehicle, self).__init__(price_tag,
                                          payment_duration=payment_duration)
        self.type = 'ICE Vehicle'
        self.gas_price_per_gallon = 2.50
        self.miles_per_gallon = mpg
        
        self.energy_ppm = self.gas_price_per_gallon / self.miles_per_gallon
        
        # Add in oil changes, $40 per 5,000 miles
        self.add_maintenance_cost(40, 5000)
        # Add the energy cost into the moving price per miles
        self.add_energy_cost()
        
class electric_vehicle(vehicle):
    """ This is an electric vehicle with assistance in calculating the
    cost of ownership parameters
    """
    
    def __init__(self, price_tag, battery_size_kwh, range_mi,
                 payment_duration=None):
        super(electric_vehicle, self).__init__(price_tag,
                                         payment_duration=payment_duration)
        self.type = 'Electric Vehicle'
        self.range = range_mi
        self.battery_size = battery_size_kwh
        self.update_energy_ppm(0.13) # Default to $0.13 per kwh
        
        # Add the energy cost into the moving price per miles
        self.add_energy_cost()
        
    def update_energy_ppm(self, electricity_cost):
        """ Updating the energy price of traveling per mile"""
        
        self.price_per_kwh = electricity_cost
        self.miles_per_kwh = self.range / self.battery_size
        self.energy_ppm = self.price_per_kwh / self.miles_per_kwh
        
        self.add_energy_cost()
        