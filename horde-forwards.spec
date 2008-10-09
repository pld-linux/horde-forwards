%define		_hordeapp	forwards
#
%include	/usr/lib/rpm/macros.php
Summary:	forwards - user e-mail forwards module for Horde
Summary(pl.UTF-8):	forwards - moduł do ustawiania przekazywania poczty w Horde
Name:		horde-%{_hordeapp}
Version:	3.0.1
Release:	2
License:	ASL
Group:		Applications/WWW
Source0:	ftp://ftp.horde.org/pub/forwards/%{_hordeapp}-h3-%{version}.tar.gz
# Source0-md5:	0a2c16b1ff7ea80a246610d6e3ce6b50
Source1:	%{name}.conf
URL:		http://www.horde.org/forwards/
BuildRequires:	rpm-php-pearprov >= 4.0.2-98
BuildRequires:	rpmbuild(macros) >= 1.264
BuildRequires:	tar >= 1:1.15.1
Requires(post):	sed >= 4.0
Requires:	horde >= 3.0
Requires:	php(xml)
Requires:	php-common >= 3:4.1.0
Requires:	webapps
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_noautoreq	'pear(Horde.*)'

%define		hordedir	/usr/share/horde
%define		_appdir		%{hordedir}/%{_hordeapp}
%define		_webapps	/etc/webapps
%define		_webapp		horde-%{_hordeapp}
%define		_sysconfdir	%{_webapps}/%{_webapp}

%description
Forwards is a Horde module for setting user e-mail forwards with
support for several popular mailers.

Right now, Forwards provides fairly complete support for setting
.forward style forwards on Sendmail, Courier, or Qmail mail based
systems via an FTP transport. It now also has drivers for Mdaemon,
Exim SQL, Exim LDAP, Custom SQL, and SOAP based systems.

%description -l pl.UTF-8
Forwards to moduł Horde do ustawiania przekazywania poczty
elektronicznej z obsługą kilku popularnych systemów pocztowych.

Aktualnie Forwards obsługuje ustawianie przekazywania w stylu .forward
przy systemach pocztowych opartych na Sendmailu, Courierze i Qmailu
poprzez transport FTP. Ma także sterowniki dla systemów Mdaemon, Exim
SQL, Exim LDAP, Custom SQL i SOAP.

%prep
%setup -q -n %{_hordeapp}-h3-%{version}

rm -f {,*/}.htaccess
# considered harmful (horde/docs/SECURITY)
rm -f test.php

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},%{_appdir}/docs}

cp -a *.php $RPM_BUILD_ROOT%{_appdir}
cp -a config/* $RPM_BUILD_ROOT%{_sysconfdir}
echo '<?php ?>' > $RPM_BUILD_ROOT%{_sysconfdir}/conf.php
touch $RPM_BUILD_ROOT%{_sysconfdir}/conf.php.bak
cp -a lib locale templates themes $RPM_BUILD_ROOT%{_appdir}
cp -a docs/CREDITS $RPM_BUILD_ROOT%{_appdir}/docs

ln -s %{_sysconfdir} 	$RPM_BUILD_ROOT%{_appdir}/config
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/apache.conf
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ ! -f %{_sysconfdir}/conf.php.bak ]; then
	install /dev/null -o root -g http -m660 %{_sysconfdir}/conf.php.bak
fi

# take uids with < 500 and update refused logins in default conf.xml
USERLIST=$(awk -F: '{ if ($3 < 500) print $1 }' < /etc/passwd | xargs | tr ' ' ',')
if [ "$USERLIST" ]; then
	sed -i -e "
	# primitive xml parser ;)
	/configlist name=\"refused\"/s/>.*</>$USERLIST</
	" %{_sysconfdir}/conf.xml
fi

%triggerin -- apache1 < 1.3.37-3, apache1-base
%webapp_register apache %{_webapp}

%triggerun -- apache1 < 1.3.37-3, apache1-base
%webapp_unregister apache %{_webapp}

%triggerin -- apache < 2.2.0, apache-base
%webapp_register httpd %{_webapp}

%triggerun -- apache < 2.2.0, apache-base
%webapp_unregister httpd %{_webapp}

%files
%defattr(644,root,root,755)
%doc README docs/*
%dir %attr(750,root,http) %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf
%attr(660,root,http) %config(noreplace) %{_sysconfdir}/conf.php
%attr(660,root,http) %config(noreplace) %ghost %{_sysconfdir}/conf.php.bak
%attr(640,root,http) %{_sysconfdir}/conf.xml

%dir %{_appdir}
%{_appdir}/*.php
%{_appdir}/config
%{_appdir}/docs
%{_appdir}/lib
%{_appdir}/locale
%{_appdir}/templates
%{_appdir}/themes
