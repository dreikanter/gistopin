@echo off
set public_dir=C:\inetpub\wwwroot\gistopin
set target_dir=.\sample-feeds
echo Linking %public_dir% to %target_dir%
mklink /j %public_dir% %target_dir%