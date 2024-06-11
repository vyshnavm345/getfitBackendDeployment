#!/bin/sh
psql -h localhost -p 5432 -U postgres -d postgres < backup.sql
