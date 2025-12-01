Este proyecto escrito en python utiliza los datos de la base para generar una imagen de seguimiento para tmin, tmax y otro para la lluvia que se pueden ver

en el siguiente link: [Seguimiento PP y T](http://www.ora.gob.ar/pp_t.php)

La carpeta ***datos*** contiene el listado de estaciones para las cuales se hace seguimiento y las variables históricas de cada una de las variables meteorológicas: mediana, datos normales mensuales que se agregan en las figuras.

Para cada nuevo usuario se recomienda:

* Tener la *base datos ORA* en alguna carpeta diferente a la que se usa regularmente (hacer copia)
* modificar el archivo config_database.txt con los parametros especificos, en particular la carpeta donde se encuentra la base de datos ora.mdb
* Para correr y generar las figuras: utilizar en terminal y colocar: python *run_seguimiento_pp_t.py* ***dd-mm-yyyy*** (utilizar la fecha correspondiente)
* Eso genera una carpeta en ***./figuras/yyyymmdd/*** que despues debe ser colocada en el servidor de la web.
