#----------------------------------------------------------------------
#                                                                      
#                           CERN                                       
#                                                                      
#     European Organization for Nuclear Research                       
#                                                                      
#     
#     This file is part of the code:
#                                                                      		    
# 
#		           PyPIC Version 1.01                     
#                  
#                                                                       
#     Author and contact:   Giovanni IADAROLA 
#                           BE-ABP Group                               
#                           CERN                                       
#                           CH-1211 GENEVA 23                          
#                           SWITZERLAND  
#                           giovanni.iadarola@cern.ch                  
#                                                                      
#                contact:   Giovanni RUMOLO                            
#                           BE-ABP Group                               
#                           CERN                                      
#                           CH-1211 GENEVA 23                          
#                           SWITZERLAND  
#                           giovanni.rumolo@cern.ch                    
#                                                                      
#
#                                                                      
#     Copyright  CERN,  Geneva  2011  -  Copyright  and  any   other   
#     appropriate  legal  protection  of  this  computer program and   
#     associated documentation reserved  in  all  countries  of  the   
#     world.                                                           
#                                                                      
#     Organizations collaborating with CERN may receive this program   
#     and documentation freely and without charge.                     
#                                                                      
#     CERN undertakes no obligation  for  the  maintenance  of  this   
#     program,  nor responsibility for its correctness,  and accepts   
#     no liability whatsoever resulting from its use.                  
#                                                                      
#     Program  and documentation are provided solely for the use  of   
#     the organization to which they are distributed.                  
#                                                                      
#     This program  may  not  be  copied  or  otherwise  distributed   
#     without  permission. This message must be retained on this and   
#     any other authorized copies.                                     
#                                                                      
#     The material cannot be sold. CERN should be  given  credit  in   
#     all references.                                                  
#----------------------------------------------------------------------

import numpy as np
import rhocompute as rhocom
import int_field_for as iff
from abc import abstractmethod, ABCMeta

na = lambda x:np.array([x])

qe=1.602176565e-19;
eps0=8.8541878176e-12;

class PyPIC_Scatter_Gather(object):
	
	__metadata__ = ABCMeta
	
	def __init__(self, x_aper=None, y_aper=None, Dh=None, xg=None, yg=None, *args, **kwargs):
		print 'PyPIC Version 1.01'
		
		if xg!=None and xg!=None:
			assert(x_aper==None and y_aper==None and Dh==None)
			Nxg=len(xg);
			bias_x=min(xg);

			Nyg=len(yg);
			bias_y=min(yg);
			
			Dh = xg[1]-xg[0]
		else:
			assert(xg==None and xg==None)
			xg=np.arange(0, x_aper+5.*Dh,Dh,float)  
			xgr=xg[1:]
			xgr=xgr[::-1]#reverse array
			xg=np.concatenate((-xgr,xg),0)
			Nxg=len(xg);
			bias_x=min(xg);

			yg=np.arange(0,y_aper+4.*Dh,Dh,float)  
			ygr=yg[1:]
			ygr=ygr[::-1]#reverse array
			yg=np.concatenate((-ygr,yg),0)
			Nyg=len(yg);
			bias_y=min(yg);

		self.Dh=Dh
		self.xg = xg
		self.Nxg = Nxg
		self.bias_x = bias_x
		self.yg = yg
		self.Nyg = Nyg
		self.bias_y = bias_y

                        
	#@profile
	def scatter(self, x_mp, y_mp, nel_mp, charge = -qe):
		
		if not (len(x_mp)==len(y_mp)==len(nel_mp)):
			raise ValueError('x_mp, y_mp, nel_mp should have the same length!!!')
		
		if len(x_mp)>0:
			rho=rhocom.compute_sc_rho(x_mp,y_mp,nel_mp,
									  self.bias_x,self.bias_y,self.Dh, self.Nxg, self.Nyg)

			self.rho=charge*rho/(self.Dh*self.Dh);
		else:
			self.rho=self.rho*0.

         
	def gather(self, x_mp, y_mp):
		
		if not (len(x_mp)==len(y_mp)):
			raise ValueError('x_mp, y_mp should have the same length!!!')

		if len(x_mp)>0:    
			## compute beam electric field
			Ex_sc_n, Ey_sc_n = iff.int_field(x_mp,y_mp,self.bias_x,self.bias_y,self.Dh,
										 self.Dh, self.efx, self.efy)
					   
		else:
			Ex_sc_n=0.
			Ey_sc_n=0.
			
		return Ex_sc_n, Ey_sc_n

	@abstractmethod
	def solve(self, *args, **kwargs):
		'''Computes the electric field maps from the stored 
		charge distribution (self.rho) and stores them in
		self.efx, self.efy.'''
		pass
		
	#@profile
	def scatter_and_solve(self, x_mp, y_mp, nel_mp, charge = -qe):
		self.scatter(x_mp, y_mp, nel_mp, charge)
		self.solve()
