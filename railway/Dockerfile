# ------------------------------------------
# - Stage: 01 - builder
# ------------------------------------------

# This image is also based on frappe/bench which we use for production
# https://github.com/pipech/erpnext-docker-debian/blob/master/Dockerfile
# Pinned by digest, not just the :version-15-latest tag. That tag is rebuilt
# upstream on a weekly schedule, so an unpinned build could silently pull a
# different ERPNext version than the one this deployment was verified against.
# Digest below == the image behind :version-15-latest at time of pinning, and
# is the exact base of the currently running production deployment.
# To upgrade: bump the digest deliberately, then redeploy and test.
FROM pipech/erpnext-docker-debian:version-15-latest@sha256:4cfc2499c43f93e2fed79358ed8e349e75840e8889d5d99a67c0a9f6cd04e542 AS builder

# These variable has been set from base image
# $systemUser, $benchFolderName
USER $systemUser
WORKDIR /home/$systemUser/$benchFolderName

# bin_tracking is a local, uncommitted-to-its-own-repo app folder, so it is
# copied in rather than fetched with `bench get-app` (which requires a git repo)
COPY --chown=frappe:frappe /bin_tracking /tmp/bin_tracking

RUN echo "-> Start builder" \
    ### remove unused sites, created by base image
    && rm -rf /home/$systemUser/$benchFolderName/sites/site1.local \
    ### [HOTFIX] Railway used IPv6 (Does not support IPv4),  https://docs.railway.com/guides/private-networking#caveats
    ### https://github.com/frappe/frappe/issues/33981
    && sed -i 's/socket\.AF_INET, socket\.SOCK_STREAM/socket.AF_INET6, socket.SOCK_STREAM/g' /home/frappe/bench/apps/frappe/frappe/utils/connections.py \
    ### install your custom apps here
    # && bench get-app https://github.com/your-repo/custom_app
    ### India GST compliance (CGST/SGST/IGST automation, GSTR reports, e-Invoice, e-Way Bill)
    ### Pinned to v15.30.1: it requires ERPNext >= 15.60.0, which the base image
    ### (15.91.3) satisfies. v15.30.2+ require ERPNext >= 15.113.0 and refuse to install.
    && bench get-app --branch v15.30.1 --resolve-deps https://github.com/resilient-tech/india-compliance \
    ### Warehouse bin tracking (QR/barcode) — local app, installed manually
    && cp -r /tmp/bin_tracking apps/bin_tracking \
    # register the app at bench level so `bench build` / `bench install-app` see it.
    # printf with a leading \n (not `echo`): get-app can leave apps.txt without a
    # trailing newline, which would glue the name onto the previous entry.
    # The sed then strips any blank line that leading \n may have introduced.
    && printf '\nbin_tracking\n' >> sites/apps.txt \
    && sed -i '/^$/d' sites/apps.txt \
    # Install runtime deps explicitly, then the app itself with --no-deps.
    # Without --no-deps, pip would try to resolve the "frappe"/"erpnext" entries
    # in setup.py's install_requires from PyPI (unrelated packages) and could
    # clobber the bench's editable installs.
    && env/bin/pip install --no-cache-dir qrcode Pillow \
    && env/bin/pip install --no-cache-dir -e apps/bin_tracking --no-deps \
    && echo "-> apps.txt now contains:" && cat sites/apps.txt \
    && echo "-> Builder done!"


# ------------------------------------------
# - Stage: 02 - production
# ------------------------------------------

# Image version should also match with stage 01
# (Check pipech/erpnext-docker-debian Dockerfile)
# https://github.com/frappe/frappe_docker/blob/main/images/bench/Dockerfile
# Digest-pinned for the same reason as the builder stage above; the tag alone
# is mutable. Must stay in step with the builder image (see note there).
FROM frappe/bench:v5.22.9@sha256:1125a56f0b9395addf90f054fd986d0ab62ceabc16fe865cad2fe0e8c2df782e

# this env should match stage 01
# (Check pipech/erpnext-docker-debian Dockerfile)
ENV systemUser=frappe
ENV benchFolderName=bench

# Copied bench folder from build stage
COPY --from=builder --chown=$systemUser /home/$systemUser/$benchFolderName /home/$systemUser/$benchFolderName

# Copy template
COPY /railway/temp_nginx.conf /home/$systemUser/temp_nginx.conf
COPY /railway/temp_supervisor.conf /home/$systemUser/temp_supervisor.conf

USER root
WORKDIR /home/$systemUser/$benchFolderName

# [fix] "debconf: unable to initialize frontend: Dialog"
# https://github.com/moby/moby/issues/27988
ARG DEBIAN_FRONTEND=noninteractive

RUN echo "-> Install nginx & supervisor" \
    # apt-get update
    && apt-get update \
    && apt-get install -y \
    # nginx for serving files
    nginx \
    # supervisor to run multiple server per container
    supervisor \
    && echo "-> Cleaning installation" \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && echo "-> Remove nginx default site" \
    && rm /etc/nginx/sites-enabled/default \
    && echo "-> Rebuilding bench" \
    && su $systemUser -c "bench build" \
    && su $systemUser -c "cp -r /home/$systemUser/$benchFolderName/sites /home/$systemUser/$benchFolderName/built_sites"

COPY --chown=$systemUser --chmod=0755 /railway/railway-setup.sh /home/$systemUser/$benchFolderName/railway-setup.sh
COPY --chown=$systemUser --chmod=0755 /railway/railway-entrypoint.sh /usr/local/bin/railway-entrypoint.sh
COPY --chown=$systemUser --chmod=0755 /railway/railway-cmd.sh /usr/local/bin/railway-cmd.sh

ENTRYPOINT ["/usr/local/bin/railway-entrypoint.sh"]
CMD ["/usr/local/bin/railway-cmd.sh"]

EXPOSE 80
