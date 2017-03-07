
# coding: utf-8

# In[7]:

import create_index


# In[8]:

create_index.create_index("localhost:9200")


# In[1]:

import export_to_es


# In[2]:

export_to_es.walk_path("/tmp/newscruncher/fr")


# In[ ]:



