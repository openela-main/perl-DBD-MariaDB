# Disable leak tests
%bcond_with perl_DBD_MariaDB_enables_leak_test
# Perform optional net_ssleay tests
%if 0%{?rhel}
%bcond_with perl_DBD_MariaDB_enables_net_ssleay_test
%else
%bcond_without perl_DBD_MariaDB_enables_net_ssleay_test
%endif

Name:           perl-DBD-MariaDB
Version:        1.21
Release:        16%{?dist}
Summary:        MariaDB and MySQL driver for the Perl5 Database Interface (DBI)
License:        GPL+ or Artistic
URL:            https://metacpan.org/release/DBD-MariaDB/
Source0:        https://cpan.metacpan.org/authors/id/P/PA/PALI/DBD-MariaDB-%{version}.tar.gz
Source1:        test-setup.t
Source2:        test-clean.t
Source3:        test-env.sh
Patch0:         DBD-MariaDB-1.21-Run-test-setup-and-clean.patch
# Fix test for changed value of mariadb_clientversion
# mariadb-connector-c 3.2.x version number changed mariadb_clientversion to 3020x
Patch1:         DBD-MariaDB-fix-mariadb-connector-c-32x-test.patch
BuildRequires:  findutils
BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  mariadb-connector-c
BuildRequires:  mariadb-connector-c-devel
BuildRequires:  openssl-devel
BuildRequires:  perl-devel
BuildRequires:  perl-generators
BuildRequires:  perl-interpreter
BuildRequires:  perl(:VERSION) >= 5.8.1
BuildRequires:  perl(Config)
BuildRequires:  perl(Data::Dumper)
BuildRequires:  perl(DBI) >= 1.608
BuildRequires:  perl(DBI::DBD)
BuildRequires:  perl(Devel::CheckLib) >= 1.12
BuildRequires:  perl(DynaLoader)
BuildRequires:  perl(ExtUtils::MakeMaker) >= 6.76
BuildRequires:  perl(File::Spec)
BuildRequires:  perl(Getopt::Long)
BuildRequires:  perl(strict)
BuildRequires:  perl(utf8)
BuildRequires:  perl(warnings)
# Tests
BuildRequires:  hostname
BuildRequires:  mariadb
BuildRequires:  mariadb-server
BuildRequires:  perl(B)
BuildRequires:  perl(bigint)
BuildRequires:  perl(constant)
# Required to process t/testrules.yml
BuildRequires:  perl(CPAN::Meta::YAML)
BuildRequires:  perl(DBI::Const::GetInfoType)
BuildRequires:  perl(Encode)
BuildRequires:  perl(File::Path)
BuildRequires:  perl(File::Temp)
BuildRequires:  perl(FindBin)
BuildRequires:  perl(lib)
BuildRequires:  perl(Test::Deep)
BuildRequires:  perl(Test::More) >= 0.90
BuildRequires:  perl(Time::HiRes)
BuildRequires:  perl(vars)
# Optional tests
%if %{with perl_DBD_MariaDB_enables_net_ssleay_test}
BuildRequires:  perl(Net::SSLeay)
%endif
%if %{with perl_DBD_MariaDB_enables_leak_test}
BuildRequires:  perl(Proc::ProcessTable)
BuildRequires:  perl(Storable)
%endif

Requires:       perl(:MODULE_COMPAT_%(eval "`perl -V:version`"; echo $version))

# Filter private modules for tests
%global __requires_exclude %{?__requires_exclude:%__requires_exclude|}perl\\(lib.pl\\)

%description
DBD::MariaDB is the Perl5 Database Interface driver for MariaDB and MySQL
databases. In other words: DBD::MariaDB is an interface between the Perl
programming language and the MariaDB/MySQL programming API that comes with
the MariaDB/MySQL relational database management system. Most functions
provided by this programming API are supported. Some rarely used functions
are missing, mainly because no-one ever requested them.

%package tests
Summary:        Tests for %{name}
Requires:       %{name} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       perl-Test-Harness
Requires:       hostname
Requires:       mariadb
Requires:       mariadb-server
# Required to process t/testrules.yml
Requires:       perl(CPAN::Meta::YAML)
# Optional tests
%if %{with perl_DBD_MariaDB_enables_net_ssleay_test}
Requires:       perl(Net::SSLeay)
%endif
%if %{with perl_DBD_MariaDB_enables_leak_test}
Requires:       perl(Proc::ProcessTable)
Requires:       perl(Storable)
%endif

%description tests
Tests from %{name}. Execute them
with "%{_libexecdir}/%{name}/test".

%prep
%setup -q -n DBD-MariaDB-%{version}
%patch0 -p1
%patch1 -p1
cp %{SOURCE1} %{SOURCE2} t/

# Help file to recognise the Perl scripts and normalize shebangs
for F in t/*.t t/*.pl; do
    perl -i -MConfig -ple 'print $Config{startperl} if $. == 1 && !s{\A#!.*perl\b}{$Config{startperl}}' "$F"
    chmod +x "$F"
done

# Remove release tests
for F in t/pod.t t/manifest.t; do
    rm "$F"
    perl -i -ne 'print $_ unless m{^\Q'"$F"'\E}' MANIFEST
    perl -i -ne 'print $_ unless m{\Q'"$F"'\E}' t/testrules.yml
done

%if %{without perl_DBD_MariaDB_enables_leak_test}
# Remove unused tests
for F in t/60leaks.t t/rt86153-reconnect-fail-memory.t; do
    rm "$F"
    perl -i -ne 'print $_ unless m{^\Q'"$F"'\E}' MANIFEST
    perl -i -ne 'print $_ unless m{\Q'"$F"'\E}' t/testrules.yml
done
%endif

%build
perl Makefile.PL INSTALLDIRS=vendor OPTIMIZE="$RPM_OPT_FLAGS" NO_PACKLIST=1 NO_PERLLOCAL=1
%{make_build}

%install
%{make_install}
find $RPM_BUILD_ROOT -type f -name '*.bs' -size 0 -delete

# Install tests
mkdir -p %{buildroot}%{_libexecdir}/%{name}
cp -a t %{buildroot}%{_libexecdir}/%{name}
cp %{SOURCE3} %{buildroot}%{_libexecdir}/%{name}
cat > %{buildroot}%{_libexecdir}/%{name}/test << EOF
#!/bin/sh
unset RELEASE_TESTING
. %{_libexecdir}/%{name}/$(basename %{SOURCE3})
cd %{_libexecdir}/%{name} && exec prove -I .
EOF
chmod +x %{buildroot}%{_libexecdir}/%{name}/test

%{_fixperms} $RPM_BUILD_ROOT/*

%check
# Set MariaDB and DBD::MariaDB test environment
. %{SOURCE3}

unset RELEASE_TESTING
make test %{?with_perl_DBD_MariaDB_enables_leak_test:EXTENDED_TESTING=1}

%files
%license LICENSE
%doc Changes Changes.historic
%{perl_vendorarch}/auto/*
%{perl_vendorarch}/DBD*
%{_mandir}/man3/*

%files tests
%{_libexecdir}/%{name}

%changelog
* Thu Feb 17 2022 Jitka Plesnikova <jplesnik@redhat.com> - 1.21-16
- Fix test for mariadb-connector-c 3.2.x

* Tue Aug 17 2021 Jitka Plesnikova <jplesnik@redhat.com> - 1.21-15
- Related: rhbz#1960259 - Enable gating

* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com> - 1.21-14
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Tue Jun 22 2021 Mohan Boddu <mboddu@redhat.com> - 1.21-13
- Rebuilt for RHEL 9 BETA for openssl 3.0
  Related: rhbz#1971065

* Tue May 04 2021 Jitka Plesnikova <jplesnik@redhat.com> - 1.21-12
- Update tests

* Fri Mar 12 2021 Jitka Plesnikova <jplesnik@redhat.com> - 1.21-11
- Package tests

* Wed Jan 27 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1.21-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.21-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Tue Jun 23 2020 Jitka Plesnikova <jplesnik@redhat.com> - 1.21-8
- Perl 5.32 rebuild

* Fri Apr 17 2020 Jitka Plesnikova <jplesnik@redhat.com> - 1.21-7
- Update setup script due to Pali's comments

* Tue Feb 04 2020 Jitka Plesnikova <jplesnik@redhat.com> - 1.21-6
- Update setup script to work with MariaDB 10.4

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.21-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Fri Jul 26 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.21-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Wed Jul 10 2019 Jitka Plesnikova <jplesnik@redhat.com> - 1.21-3
- Run setup as part of tests

* Wed Jun 26 2019 Jitka Plesnikova <jplesnik@redhat.com> - 1.21-2
- Enable tests

* Thu Jun 13 2019 Jitka Plesnikova <jplesnik@redhat.com> - 1.21-1
- Specfile autogenerated by cpanspec 1.78.
