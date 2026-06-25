# Lab Guide for Cisco Live US 2026: LTRSEC-2241

Web guide link: http://bgl-vms-vm1143.cisco.com/ltrsec-2241/

PDF guide link: http://bgl-vms-vm1143.cisco.com/ltrsec-2241/pdf/document.pdf

## Local build and hosting

The local Apache web server serves the guide from:

```text
/var/www/html/ltrsec-2241
```

On `bgl-vms-vm1143`, this path is a symlink to the MkDocs build output in this
repository:

```text
/var/www/html/ltrsec-2241 -> /home/palugu/ltrsec-2241-clamer26/site
```

To rebuild the web guide and PDF locally, run:

```bash
cd /home/palugu/ltrsec-2241-clamer26
. .venv/bin/activate
mkdocs build --clean
```

After the build completes, Apache serves the updated files automatically because
the web root points directly at the `site/` directory. No `rsync` step is needed.

Expected generated outputs:

```text
site/index.html
site/pdf/document.pdf
```
