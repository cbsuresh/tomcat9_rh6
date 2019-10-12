# RPM SPEC file to build tomcat9 on RHEL6
%define __jar_repack %{nil}
%define debug_package %{nil}
%define tomcat_home /opt/tomcat9
%define tomcat_user_home /home/tomcat
%define tomcat_group tomcat
%define tomcat_user tomcat
%define tomcat_uid 790
%define tomcat_gid 790

# distribution specific definitions
%define use_systemd (0%{?rhel} && 0%{?rhel} >= 7)

%if 0%{?rhel}  == 6
Requires(pre): shadow-utils
Requires: initscripts >= 8.36
Requires(post): chkconfig
%endif

%if 0%{?rhel}  == 7
Requires(pre): shadow-utils
Requires: systemd
BuildRequires: systemd
%endif

# end of distribution specific definitions

Summary:    Apache Servlet/JSP Engine
Name:       tomcat
Version:    9.0.24
Release:    1%{?dist}
BuildArch:  noarch
License:    Apache 
Group:      Applications/Internet
URL:        https://tomcat.apache.org/
Vendor:     Apache Software Foundation
Packager:   Suresh Babu Chorampalli Bharat <schorampalli@usda.gov>
Source0:    apache-tomcat-%{version}.tar.gz
Source1:    %{name}.init
Source2:    %{name}.sysconfig
Source3:    %{name}.logrotate
Requires:   jre >= 1.8 
BuildRoot:  %{_tmppath}/tomcat-%{version}-%{release}-root-%(%{__id_u} -n)

Provides: tomcat
Provides: tomcat9

%description
Tomcat is the servlet container that is used in the official Reference
Implementation for the Java Servlet and JavaServer Pages technologies.
The Java Servlet and JavaServer Pages specifications are developed by
Sun under the Java Community Process.


%prep
%setup -q -n apache-tomcat-%{version}

%build

%install
install -d -m 755 %{buildroot}/%{tomcat_home}/
cp -R * %{buildroot}/%{tomcat_home}/

# Clean webapps Put webapps in app/tomcat/webapps and link back --WEBAPPS--.
mkdir -p /app/tomcat/webapps
# chown -R %{tomcat_uid}.%{tomcat_group} /app/%{name}
cp -Rp /opt/tomcat9/webapps/* /app/tomcat/webapps 2 > /dev/null || :
/bin/rm -rf %{buildroot}/%{tomcat_home}/webapps/
install -d -m 755 %{buildroot}%{tomcat_home}/webapps
cd %{buildroot}/%{tomcat_home}/
/bin/rm -rf webapps
ln -s /app/%{name}/webapps webapps
cd -

# Put logging in /var/log and link back ---LOGGING---.
rm -rf %{buildroot}/%{tomcat_home}/logs
install -d -m 755 %{buildroot}/var/log/%{name}/
cd %{buildroot}/%{tomcat_home}/
ln -s /var/log/%{name}/ logs
cd -

# Remove *.bat -->BAT files for Windows Installs--.
rm -f %{buildroot}/%{tomcat_home}/bin/*.bat

# Put conf in /etc/ and link back.
install -d -m 755 %{buildroot}/%{_sysconfdir}
mv %{buildroot}/%{tomcat_home}/conf %{buildroot}/%{_sysconfdir}/%{name}
cd %{buildroot}/%{tomcat_home}/
ln -s %{_sysconfdir}/%{name} conf
cd -

# Remove *.bat    
rm -f %{buildroot}/%{tomcat_home}/bin/*.bat


# Drop init script
install -d -m 755 %{buildroot}/%{_initrddir}
install    -m 755 %_sourcedir/%{name}.init %{buildroot}/%{_initrddir}/%{name}

# Drop sysconfig script
install -d -m 755 %{buildroot}/%{_sysconfdir}/sysconfig/
install    -m 644 %_sourcedir/%{name}.sysconfig %{buildroot}/%{_sysconfdir}/sysconfig/%{name}

# Drop logrotate script
install -d -m 755 %{buildroot}/%{_sysconfdir}/logrotate.d
install    -m 644 %_sourcedir/%{name}.logrotate %{buildroot}/%{_sysconfdir}/logrotate.d/%{name}


%clean
rm -rf %{buildroot}

%pre
mkdir -p %{tomcat_user_home}
getent group %{tomcat_group} >/dev/null || groupadd -r %{tomcat_group} -g %{tomcat_gid} 
getent passwd %{tomcat_user} >/dev/null || /usr/sbin/useradd --comment "Tomcat Daemon User" --shell /sbin/nologin -M -r -g %{tomcat_group} -u %{tomcat_uid} --home %{tomcat_user_home} %{tomcat_user}
chown -R %{tomcat_uid}.%{tomcat_group} %{tomcat_user_home}
chmod 700 %{tomcat_user_home}

%files
%defattr(-,%{tomcat_user},%{tomcat_group})
%{tomcat_home}/*
/var/log/%{name}/

%defattr(-,root,root)
%{_initrddir}/%{name}
%{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/*


%post
chkconfig --add %{name}
chkconfig --level 2345 tomcat on
chown -R %{tomcat_uid}.%{tomcat_group} /var/log/%{name}
chown -R %{tomcat_uid}.%{tomcat_group} /app/%{name}
cat <<BANNER
---------------------------------------------------------------------------------

Please find the official documentation for tomcat here:
* https://tomcat.apache.org/

Apache Tomcat RN for %{name}.%{version} on RHEL6 completed Install successfully.
---------------------------------------------------------------------------------
BANNER


%preun
if [ $1 = 0 ]; then
  service %{name} stop > /dev/null 2>&1
  chkconfig --del %{name}
fi

%postun
if [ $1 -ge 1 ]; then
  service %{name} condrestart >/dev/null 2>&1
fi
/usr/sbin/userdel -f %{name}
/bin/rm -rf %{tomcat_home}

%changelog
* Sat Oct 8 2019 Suresh Chorampalli  <schorampalli@usda.gov>
- Initial release Tomcat 9.0.24.
