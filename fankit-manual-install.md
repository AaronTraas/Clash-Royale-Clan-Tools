# Fan Kit Manual Install

If you've had issues with crtools downloading and extracting the fan kit, try
the following:

1. In your config file, add line `use_fankit=True` to the `[Paths]` section
2. Download the fan kit from <https://supr.cl/CRFanKit>
3. Extract the fan kit
4. Create an empty folder called `fankit` in your output folder (specified in
   your `out` property in the `[Paths]` section)
5. Copy the following folders to the `fankit` folder from the unzipped fan kit
	- `emotes`
	- `font`
	- `ui`
6. Make sure the folder, subfolders, and files have the correct permissions the be
   read by the web server. If not, correct them.
7. Run `crtools`

You're know you are successful if the site renders using the official Clash
Royale font

## Correcting permissions

Assuming a Linux web server, the files and folders typically need to be group
and world readable. To do that, assuming the path to your document root is
`/var/www/html`, type:

```
chmod -R chmod -R g+r,o+r /var/www/html/fankit
```

Each time crtools runs, it will copy the old fan kit including the permissions,
so you should only need to do this once.